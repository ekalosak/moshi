# IP addr. provisioned here so it can remain static across changes to other server infra.

provider "google-beta" {
  project = "moshi-3"
}

resource "google_compute_global_address" "default" {
  # https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_global_address
  provider     = google-beta
  project      = "moshi-3"
  name         = "moshi-srv-ip"
  description  = "This IP address is used by the Moshi media server load balancer."
  purpose      = "GLOBAL"
  address_type = "EXTERNAL"
  labels = {
    environment = "dev"
  }
}

output "moshi-srv-external-ip" {
  value = google_compute_global_address.default.address
}