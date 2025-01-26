resource "google_cloud_scheduler_job" "process_image_trigger" {
  name        = "process-image-trigger"
  description = "Trigger Cloud Function to process images daily at 5 AM CET"
  schedule    = "0 5 * * *" # Cron format for 5 AM daily in UTC (CET = UTC+1 or +2 during DST)

  time_zone   = "Europe/Stockholm" # Set to CET timezone

  http_target {
    uri         = google_cloudfunctions2_function.process_image.service_config[0].uri
    http_method = "POST"

    oidc_token {
      service_account_email = google_service_account.process_image_scheduler.email
    }
  }

  depends_on = [
    google_cloudfunctions2_function.process_image
  ]
}

resource "google_service_account" "process_image_scheduler" {
  account_id   = "process-image-scheduler"
  display_name = "Service Account for Cloud Scheduler to trigger Cloud Function"
}

resource "google_project_iam_member" "process_image_invoker" {
  project = var.project_id
  role    = "roles/cloudfunctions.invoker"
  member  = "serviceAccount:${google_service_account.process_image_scheduler.email}"
}