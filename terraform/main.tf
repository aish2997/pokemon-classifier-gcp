provider "google" {
  project = var.project_id
  region  = "europe-west1"
}

provider "kubernetes" {
  load_config_file = true
}
