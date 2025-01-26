resource "google_bigquery_dataset" "image_data" {
  dataset_id = var.bigquery_dataset_name
  location   = var.region
}

resource "google_bigquery_table" "image_classifications" {
  dataset_id = google_bigquery_dataset.image_data.dataset_id
  table_id   = var.bigquery_table_name

  schema = jsonencode([
    {
      name = "file_name"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "class_label"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "description"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "score"
      type = "FLOAT"
      mode = "REQUIRED"
    },
    {
      name = "timestamp"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    }
  ])
}