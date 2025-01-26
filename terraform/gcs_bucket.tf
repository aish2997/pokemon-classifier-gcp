resource "google_storage_bucket" "image_bucket" {
  name          = var.gcs_bucket_name
  location      = var.region
  storage_class = "STANDARD"
}