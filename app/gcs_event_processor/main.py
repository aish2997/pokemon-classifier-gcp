import functions_framework
# from google.cloud import storage, bigquery
# import requests
# import json
# import base64

@functions_framework.http
def process_image(event, context):
    # bucket_name = event['bucket']
    # file_name = event['name']

    # # Initialize GCS client
    # client = storage.Client()
    # bucket = client.bucket(bucket_name)
    # blob = bucket.blob(file_name)
    # img_data = blob.download_as_bytes()

    # # Call the image classifier API
    # response = requests.post(
    #     "https://<CLOUD_RUN_URL>/classify",
    #     files={"image": img_data}
    # )
    # result = response.json()

    # # Save results to BigQuery
    # bq_client = bigquery.Client()
    # table_id = "<PROJECT_ID>.<DATASET>.<TABLE>"
    # rows_to_insert = [{
    #     "file_name": file_name,
    #     "class_label": result["class"],
    #     "description": result["description"],
    #     "score": result["score"],
    #     "timestamp": context.timestamp
    # }]
    # bq_client.insert_rows_json(table_id, rows_to_insert)
    # print(f"Processed {file_name}, saved to BigQuery.")
    return True