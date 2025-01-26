resource "google_cloudfunctions2_function" "process_image" {
  name        = "process-image"
  description = "Triggered when a new image is uploaded to the GCS bucket."
  location    = var.region # Gen2 uses `location` instead of `region`.

  build_config {
    runtime     = "python39"
    entry_point = "process_images" # Ensure this matches the Python function
    source {
      storage_source {
        bucket = "pokemon-classifier-d-state"
        object = "gcs_event_processor.zip"
      }
    }
  }

  service_config {
    available_memory   = "512Mi" # Memory specification in Gen2
    min_instance_count = 0       # Default scaling
    max_instance_count = 3000    # Adjust scaling needs

    environment_variables = { # Moved environment variables here
      CLOUD_RUN_URL   = google_cloud_run_service.image_classifier.status[0].url
      GCS_BUCKET_NAME = google_storage_bucket.image_bucket.name
      BQ_TABLE_ID     = "${google_bigquery_dataset.image_data.dataset_id}.${google_bigquery_table.image_classifications.table_id}"
    }
  }

  depends_on = [
    google_storage_bucket.image_bucket,
    google_bigquery_table.image_classifications
  ]
}