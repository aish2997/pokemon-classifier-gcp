region      = "europe-west1"
environment = "dev"

cloud_run_name = "image-classifier"

gcs_bucket_name       = "pokemon-classifier-d-image-upload-bucket"
pubsub_topic_name     = "image-processing-topic"
bigquery_dataset_name = "image_data"
bigquery_table_name   = "image_classifications"