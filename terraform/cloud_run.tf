resource "google_cloud_run_service" "image_classifier" {
  name     = var.cloud_run_name
  location = var.region

  template {
    spec {
      containers {
        #image = "gcr.io/${var.project_id}/${var.cloud_run_name}:v1"
        image = var.docker_image
        resources {
          limits = {
            memory = "4Gi"
            cpu    = "1"
          }
        }
      }
    }
  }

  autogenerate_revision_name = true

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_member" "allow_all" {
  service  = google_cloud_run_service.image_classifier.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}