resource "google_storage_bucket_notification" "gcs_to_pubsub" {
  bucket         = var.gcs_bucket_name
  topic          = google_pubsub_topic.image_processing.id
  payload_format = "JSON_API_V1"
}

resource "google_cloudfunctions_function" "process_image" {
  name        = "process-image"
  description = "Triggered when a new image is uploaded to the GCS bucket."
  runtime     = "python39"
  region      = var.region

  available_memory_mb   = 512
  source_archive_bucket = var.gcs_bucket_name
  source_archive_object = "gcs_event_processor.zip"

  entry_point = "process_image"

  environment_variables = {
    CLOUD_RUN_URL = google_cloud_run_service.image_classifier.status[0].url
  }

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.image_processing.name
  }
}