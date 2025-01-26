resource "google_storage_bucket" "image_bucket" {
  name          = var.gcs_bucket_name
  location      = var.region
  storage_class = "STANDARD"
}

resource "google_storage_notification" "gcs_to_pubsub" {
  bucket         = google_storage_bucket.image_bucket.name
  topic          = google_pubsub_topic.image_processing.id
  event_types    = ["OBJECT_FINALIZE"]
  payload_format = "JSON_API_V1"
}