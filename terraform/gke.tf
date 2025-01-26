# Create GKE cluster
resource "google_container_cluster" "primary" {
  name               = "ml-classifier-cluster"
  location           = var.region
  initial_node_count = 1

  node_config {
    machine_type = "e2-medium"

    oauth_scopes = [
      "https://www.googleapis.com/auth/devstorage.read_write",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/service.management.readonly",
      "https://www.googleapis.com/auth/trace.append"
    ]
  }

  workload_identity_config {
    identity_namespace = "${var.project_id}.svc.id.goog"
  }
}

# Kubernetes Namespace
resource "kubernetes_namespace" "ml_services" {
  metadata {
    name = "ml-services"
  }
}

# Deploy GCS Fetcher Service
resource "kubernetes_deployment" "gcs_fetcher" {
  metadata {
    name      = "gcs-fetcher"
    namespace = kubernetes_namespace.ml_services.metadata[0].name
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "gcs-fetcher"
      }
    }

    template {
      metadata {
        labels = {
          app = "gcs-fetcher"
        }
      }

      spec {
        containers {
          name  = "gcs-fetcher"
          image = var.gcs_fetcher_image

          env {
            name  = "CLOUD_RUN_URL"
            value = var.cloud_run_url
          }

          env {
            name  = "GCS_BUCKET_NAME"
            value = var.gcs_bucket_name
          }

          env {
            name  = "BQ_TABLE_ID"
            value = var.bq_table_id
          }
        }
      }
    }
  }
}

# Deploy Image Classifier Service
resource "kubernetes_deployment" "image_classifier" {
  metadata {
    name      = "image-classifier"
    namespace = kubernetes_namespace.ml_services.metadata[0].name
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "image-classifier"
      }
    }

    template {
      metadata {
        labels = {
          app = "image-classifier"
        }
      }

      spec {
        containers {
          name  = "image-classifier"
          image = var.image_classifier_image
          resources {
            limits = {
              memory = "2Gi"
              cpu    = "1"
            }
          }
        }
      }
    }
  }
}

# Expose Services via LoadBalancer
resource "kubernetes_service" "gcs_fetcher_service" {
  metadata {
    name      = "gcs-fetcher-service"
    namespace = kubernetes_namespace.ml_services.metadata[0].name
  }

  spec {
    selector = {
      app = "gcs-fetcher"
    }

    type = "LoadBalancer"

    port {
      port        = 80
      target_port = 8080
    }
  }
}

resource "kubernetes_service" "image_classifier_service" {
  metadata {
    name      = "image-classifier-service"
    namespace = kubernetes_namespace.ml_services.metadata[0].name
  }

  spec {
    selector = {
      app = "image-classifier"
    }

    type = "LoadBalancer"

    port {
      port        = 80
      target_port = 8080
    }
  }
}
