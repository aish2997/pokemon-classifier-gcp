resource "google_cloudfunctions2_function" "process_image" {
  name        = "process-image"
  description = "Triggered when a new image is uploaded to the GCS bucket."
  location    = var.region # Gen2 uses `location` instead of `region`.
  build_config {
    runtime     = "python39"
    entry_point = "process_image"
    source {
      storage_source {
        bucket = "pokemon-classifier-d-state"
        object = "gcs_event_processor.zip"
      }
    }
    environment_variables = {
      CLOUD_RUN_URL = google_cloud_run_service.image_classifier.status[0].url
    }
  }

  service_config {
    available_memory   = "512Mi" # Memory specification in Gen2
    min_instance_count = 0       # Default scaling, you can increase if needed
    max_instance_count = 3000    # Adjust based on your scaling needs
  }

  event_trigger {
    event_type = "google.cloud.storage.object.v1.finalized" # GCS trigger for Gen2
    event_filters {
      attribute = "bucket"
      value     = google_storage_bucket.image_bucket.name
    }
    trigger_region = var.region # Specify the region for the trigger
  }

  depends_on = [
    google_storage_bucket.image_bucket,
    google_pubsub_topic.image_processing
  ]
}