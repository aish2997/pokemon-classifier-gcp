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

variable "cloud_run_name" {
  description = "Name of the Cloud Run service"
  type        = string
  default     = "image-classifier"
}

variable "docker_image" {
  description = "Docker image to deploy to Cloud Run"
  type        = string
}

variable "gcs_bucket_name" {
  description = "GCS bucket name for storing images"
  type        = string
}

variable "pubsub_topic_name" {
  description = "Pub/Sub topic name for GCS event notifications"
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