provider "google" {
  project = "moshi-3"
  region  = "us-central1"
}

resource "google_project_service" "artifacts" {
  project = "moshi-3"
  service = "artifactregistry.googleapis.com"
}

resource "google_service_account" "artifact_writer" {
  account_id   = "artifact-writer"
  display_name = "Artifact Writer Service Account for GitHub Actions"
}

resource "google_project_iam_member" "artifact_writer" {
  project = "moshi-3"
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.artifact_writer.email}"
}
