output "gcs_bucket_name" {
  value = google_storage_bucket.image_bucket.name
}

output "bigquery_table_id" {
  value = google_bigquery_table.image_classifications.table_id
}

output "cluster_name" {
  value = google_container_cluster.primary.name
}

output "cluster_endpoint" {
  value = google_container_cluster.primary.endpoint
}

output "cluster_ca_certificate" {
  value = google_container_cluster.primary.master_auth[0].cluster_ca_certificate
}