provider "google-beta" {
  project = "moshi-3"
}

resource "google_compute_managed_ssl_certificate" "default" {
  # https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_managed_ssl_certificate
  provider = google-beta
  name        = "moshi-srv-ssl"
  description = "This SSL certificate is used by the Moshi media server load balancer."

  managed {
    domains = ["dev.chatmoshi.com"]
  }
}