provider "google" {
  project = "moshi-3"
  region  = "us-central1"
}

resource "google_project_service" "artifacts" {
  project = "moshi-3"
  service = "artifactregistry.googleapis.com"
}

resource "google_service_account" "artifact_reader" {
  account_id   = "artifact-reader"
  display_name = "Artifact Reader Service Account for Packer VMs"
}

resource "google_project_iam_member" "artifact_reader" {
  project = "moshi-3"
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.artifact_reader.email}"
}
