provider "google" {
  project     = "moshi-3"
  region      = "us-central1"
  zone        = "us-central1-c"
}

resource "google_project_service" "tts" {
  project = "moshi-3"
  service = "texttospeech.googleapis.com"
}

resource "google_project_service" "speech" {
  project = "moshi-3"
  service = "speech.googleapis.com"
}

resource "google_project_service" "translate" {
  project = "moshi-3"
  service = "translate.googleapis.com"
}