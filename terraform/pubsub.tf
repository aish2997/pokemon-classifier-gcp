resource "google_pubsub_topic" "image_processing" {
  name = var.pubsub_topic_name
}