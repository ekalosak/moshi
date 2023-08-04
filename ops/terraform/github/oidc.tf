variable "project_id" {
  type        = string
  default     = "moshi-3"
  description = "GCP Project ID"
}

variable "service_account" {
  type        = string
  default     = "oidc-service-account"
  description = "Name of the GCP Service Account used by the OIDC provider"
}

resource "google_service_account" "sa" {
  project    = var.project_id
  account_id = var.service_account
}

resource "google_project_iam_member" "project" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.sa.email}"
}

module "gh_oidc" {
  source      = "terraform-google-modules/github-actions-runners/google//modules/gh-oidc"
  project_id  = var.project_id
  pool_id     = "oidc-pool"
  provider_id = "oidc-gh-provider"
  sa_mapping = {
    (var.service_account) = {
      sa_name   = google_service_account.sa.name
      attribute = "attribute.repository/user/repo"
    }
  }
}


output "pool_name" {
  description = "Pool name"
  value       = module.gh_oidc.pool_name
}

output "provider_name" {
  description = "Provider name"
  value       = module.gh_oidc.provider_name
}

output "sa_email" {
  description = "Service account email"
  value       = google_service_account.sa.email
}