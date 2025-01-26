from flask import Flask, request, jsonify
from google.cloud import storage, bigquery
import os
import requests

app = Flask(__name__)

# Get environment variables
CLOUD_RUN_URL = "https://image-classifier-fb6h7y5eka-ew.a.run.app"
GCS_BUCKET_NAME = "pokemon-classifier-d-image-upload-bucket"
BQ_TABLE_ID = "pokemon-classifier-d.image_data.image_classifications"

# Initialize GCS and BigQuery clients
storage_client = storage.Client()
bq_client = bigquery.Client()
bucket = storage_client.bucket(GCS_BUCKET_NAME)

@app.route("/process_images", methods=["POST"])
def process_images():
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
                f"{CLOUD_RUN_URL}/classify",
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
            bq_client.insert_rows_json(BQ_TABLE_ID, rows_to_insert)

            print(f"Successfully processed and saved {file_name}.")
            # Move file to archive directory
            move_blob(blob, archive_dir)

        except Exception as e:
            print(f"Error processing {file_name}: {e}")
            # Move file to error directory
            move_blob(blob, error_dir)

    return jsonify({"message": "All files in 'incoming/' processed."}), 200

def move_blob(blob, destination_dir):
    """
    Move a blob to a new directory within the same bucket.
    """
    bucket = blob.bucket
    destination_name = f"{destination_dir}{blob.name.split('/')[-1]}"
    new_blob = bucket.rename_blob(blob, destination_name)
    print(f"Moved file {blob.name} to {new_blob.name}")
