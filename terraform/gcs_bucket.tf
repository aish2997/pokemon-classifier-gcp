resource "google_storage_bucket" "image_bucket" {
  name          = var.gcs_bucket_name
  location      = var.region
  storage_class = "STANDARD"
}

# Create placeholder files for directory-like structure
resource "google_storage_bucket_object" "incoming" {
  name    = "incoming/" # Simulates a directory called 'incoming'
  bucket  = google_storage_bucket.image_bucket.name
  content = "" # Empty object
}

resource "google_storage_bucket_object" "archive" {
  name    = "archive/" # Simulates a directory called 'archive'
  bucket  = google_storage_bucket.image_bucket.name
  content = "" # Empty object
}

resource "google_storage_bucket_object" "error" {
  name    = "error/" # Simulates a directory called 'error'
  bucket  = google_storage_bucket.image_bucket.name
  content = "" # Empty object
}