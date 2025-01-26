resource "google_storage_bucket" "image_bucket" {
  name          = var.gcs_bucket_name
  location      = var.region
  storage_class = "STANDARD"
}

resource "google_storage_bucket_object" "incoming" {
  name    = "incoming/" # Simulates a directory called 'incoming'
  bucket  = google_storage_bucket.image_bucket.name
  content = "Placeholder for incoming directory" # Minimal valid content
}

resource "google_storage_bucket_object" "archive" {
  name    = "archive/" # Simulates a directory called 'archive'
  bucket  = google_storage_bucket.image_bucket.name
  content = "Placeholder for archive directory" # Minimal valid content
}

resource "google_storage_bucket_object" "error" {
  name    = "error/" # Simulates a directory called 'error'
  bucket  = google_storage_bucket.image_bucket.name
  content = "Placeholder for error directory" # Minimal valid content
}