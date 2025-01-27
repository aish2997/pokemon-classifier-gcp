import os
from google.cloud import storage, bigquery
import requests
import functions_framework

@functions_framework.http
def process_images(request):
    """
    Cloud Function to process images from a Google Cloud Storage (GCS) bucket.

    The function performs the following:
    1. Reads image files from the "incoming/" directory in the specified GCS bucket.
    2. Sends the images to an image classifier API hosted on a Cloud Run service.
    3. Stores the classification results in a BigQuery table.
    4. Moves successfully processed images to the "archive/" directory.
    5. Moves images that encounter errors during processing to the "error/" directory.

    Environment Variables:
        - CLOUD_RUN_URL: URL of the image classifier API hosted on Cloud Run.
        - GCS_BUCKET_NAME: Name of the GCS bucket containing the images.
        - BQ_TABLE_ID: ID of the BigQuery table to store classification results.

    Args:
        request (flask.Request): The HTTP request object.

    Returns:
        Tuple[str, int]: A message indicating the status of processing and an HTTP status code.
    """
    # Get environment variables
    cloud_run_url = os.getenv("CLOUD_RUN_URL")
    if not cloud_run_url:
        raise ValueError("CLOUD_RUN_URL environment variable is not set.")

    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        raise ValueError("GCS_BUCKET_NAME environment variable is not set.")

    table_id = os.getenv("BQ_TABLE_ID")
    if not table_id:
        raise ValueError("BQ_TABLE_ID environment variable is not set.")

    # Initialize GCS and BigQuery clients
    storage_client = storage.Client()
    bq_client = bigquery.Client()
    bucket = storage_client.bucket(bucket_name)

    # Define directories
    incoming_dir = "incoming/"
    archive_dir = "archive/"
    error_dir = "error/"

    # Iterate over files in the incoming directory
    blobs = bucket.list_blobs(prefix=incoming_dir)
    for blob in blobs:
        file_name = blob.name

        # Skip folders
        if file_name.endswith("/"):
            continue

        print(f"Processing file: {file_name}")

        # Download file contents
        img_data = blob.download_as_bytes()

        try:
            # Call the image classifier API
            response = requests.post(
                f"{cloud_run_url}/classify",
                files={"image": img_data}
            )
            if response.status_code != 200:
                print(f"Failed to classify {file_name}: {response.text}")
                # Move file to error directory
                move_blob(blob, error_dir)
                continue

            result = response.json()

            # Insert result into BigQuery
            rows_to_insert = [{
                "file_name": file_name,
                "class_label": result["class"],
                "description": result["description"],
                "score": result["score"],
                "timestamp": blob.time_created.isoformat()  # Use GCS object's timestamp
            }]
            bq_client.insert_rows_json(table_id, rows_to_insert)

            print(f"Successfully processed and saved {file_name}.")
            # Move file to archive directory
            move_blob(blob, archive_dir)

        except Exception as e:
            print(f"Error processing {file_name}: {e}")
            # Move file to error directory
            move_blob(blob, error_dir)

    return "All files in 'incoming/' processed.", 200


def move_blob(blob, destination_dir):
    """
    Move a blob to a new directory within the same bucket.
    """
    bucket = blob.bucket
    destination_name = f"{destination_dir}{blob.name.split('/')[-1]}"
    new_blob = bucket.rename_blob(blob, destination_name)
    print(f"Moved file {blob.name} to {new_blob.name}")