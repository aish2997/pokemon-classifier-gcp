variable "project_id" {
  type        = string
  description = "GCP project ID"
}

variable "region" {
  type        = string
  description = "GCP region"
}

variable "environment" {
  type        = string
  description = "Deployment environment (dev/test/prod)"
}

variable "gcs_bucket_name" {
  description = "GCS bucket name for storing images"
  type        = string
}

variable "bigquery_dataset_name" {
  description = "BigQuery dataset name"
  type        = string
}

variable "bigquery_table_name" {
  description = "BigQuery table name"
  type        = string
}