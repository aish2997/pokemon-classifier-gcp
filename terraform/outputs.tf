output "gcs_bucket_name" {
  value = google_storage_bucket.image_bucket.name
}

output "bigquery_table_id" {
  value = google_bigquery_table.image_classifications.table_id
}