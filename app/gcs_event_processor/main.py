import functions_framework
import os
from google.cloud import storage, bigquery
import requests

@functions_framework.http
def process_images(request):
    # Get environment variables
    cloud_run_url = os.getenv("CLOUD_RUN_URL")
    if not cloud_run_url:
        raise ValueError("CLOUD_RUN_URL environment variable is not set.")

    # Initialize GCS and BigQuery clients
    storage_client = storage.Client()
    bq_client = bigquery.Client()

    # Bucket details
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        raise ValueError("GCS_BUCKET_NAME environment variable is not set.")
    bucket = storage_client.bucket(bucket_name)

    # BigQuery Table
    table_id = os.getenv("BQ_TABLE_ID")
    if not table_id:
        raise ValueError("BQ_TABLE_ID environment variable is not set.")

    # Iterate over all files in the bucket
    blobs = bucket.list_blobs()
    for blob in blobs:
        file_name = blob.name

        # Download file contents
        img_data = blob.download_as_bytes()

        # Call the image classifier API
        response = requests.post(
            f"{cloud_run_url}/classify",
            files={"image": img_data}
        )
        if response.status_code != 200:
            print(f"Failed to classify {file_name}: {response.text}")
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
        try:
            bq_client.insert_rows_json(table_id, rows_to_insert)
            print(f"Successfully processed and saved {file_name}.")
        except Exception as e:
            print(f"Error saving {file_name} to BigQuery: {e}")

    return "All images processed.", 200