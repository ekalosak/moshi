provider "google-beta" {
  project = "moshi-3"
}

resource "google_compute_managed_ssl_certificate" "default" {
  # https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_managed_ssl_certificate
  provider    = google-beta
  name        = "moshi-ssl-cert"
  description = "This SSL certificate is used by the Moshi LB."

  managed {
    domains = ["dev.chatmoshi.com", "prod.chatmoshi.com", "stage.chatmoshi.com", "www.chatmoshi.com", "chatmoshi.com"]
  }
}