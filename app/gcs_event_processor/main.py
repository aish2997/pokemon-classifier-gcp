import os
from google.cloud import storage, bigquery
import aiohttp
import asyncio
from aiofiles import open as aio_open
from functions_framework import http


@http
async def process_images(request):
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
    blobs = list(bucket.list_blobs(prefix=incoming_dir))
    tasks = [
        process_file(blob, cloud_run_url, bq_client, table_id, archive_dir, error_dir)
        for blob in blobs
        if not blob.name.endswith("/")  # Skip folders
    ]

    # Process all files concurrently
    await asyncio.gather(*tasks)

    return "All files in 'incoming/' processed.", 200


async def process_file(blob, cloud_run_url, bq_client, table_id, archive_dir, error_dir):
    """
    Process a single file: classify it, save results to BigQuery, and move to archive/error.
    """
    file_name = blob.name
    print(f"Processing file: {file_name}")

    try:
        # Download file contents
        img_data = blob.download_as_bytes()

        # Call the image classifier API
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{cloud_run_url}/classify",
                data={"image": img_data}
            ) as response:
                if response.status != 200:
                    print(f"Failed to classify {file_name}: {await response.text()}")
                    await move_blob(blob, error_dir)
                    return

                result = await response.json()

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
        await move_blob(blob, archive_dir)

    except Exception as e:
        print(f"Error processing {file_name}: {e}")
        await move_blob(blob, error_dir)


async def move_blob(blob, destination_dir):
    """
    Move a blob to a new directory within the same bucket.
    """
    bucket = blob.bucket
    destination_name = f"{destination_dir}{blob.name.split('/')[-1]}"
    new_blob = bucket.rename_blob(blob, destination_name)
    print(f"Moved file {blob.name} to {new_blob.name}")