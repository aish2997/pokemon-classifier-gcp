output "cloud_run_url" {
  value = google_cloud_run_service.image_classifier.status[0].url
}

output "gcs_bucket_name" {
  value = google_storage_bucket.image_bucket.name
}

output "bigquery_table_id" {
  value = google_bigquery_table.image_classifications.table_id
}