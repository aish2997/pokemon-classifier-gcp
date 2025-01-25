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