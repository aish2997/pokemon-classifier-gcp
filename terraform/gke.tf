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
        container {
          name  = "gcs-fetcher"
          image = "gcs-fetcher"

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
        container {
          name  = "image-classifier"
          image = "image-classifier"
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

# Expose GCS Fetcher Service
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

# Expose Image Classifier Service
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
