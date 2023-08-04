provider "google-beta" {
  project = "moshi-3"
}

resource "google_project_service" "artifacts" {
  project = "moshi-3"
  service = "artifactregistry.googleapis.com"
}

resource "google_artifact_registry_repository" "pypi" {
  provider = google-beta

  location      = "us-central1"
  repository_id = "pypi"
  description   = "PyPi for Moshi"
  format        = "python"
}

resource "google_service_account" "artifact_reader" {
  provider = google-beta

  account_id   = "artifact-reader"
  display_name = "Artifact Reader Service Account for Packer VMs"
}

resource "google_artifact_registry_repository_iam_member" "artifact_reader" {
  provider = google-beta

  location   = google_artifact_registry_repository.pypi.location
  repository = google_artifact_registry_repository.pypi.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.artifact_reader.email}"
}

output "service_account_email" {
  value = google_service_account.artifact_reader.email
}