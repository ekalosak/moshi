# 1. image template in us-central1 that uses the latest image from the "moshi-srv" image family
# 2. Instance group in us-central1 that uses the image template 
# 3. Load balancer (ALB) in us-central1 that routes traffic to the instance group
# 4. External IP address in us-central1 that is used by the load balancer
# 5. Health check in us-central1 that is used by the load balancer against the vm's /heathz endpoint

provider "google-beta" {
  project = "moshi-3"
}

resource "google_service_account" "default" {
  provider     = google-beta
  account_id   = "moshi-srv-sa"
  display_name = "Service Account for the Moshi media server's managed instance group."
}

resource "google_project_iam_member" "default" {
  project = "moshi-3"
  role    = "roles/compute.instanceAdmin"
  member  = "serviceAccount:${google_service_account.default.email}"
}

resource "google_compute_instance_template" "default" {
  // https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_instance_template
  provider    = google-beta
  name        = "moshi-srv-template"
  description = "This template is used to create Moshi media server instances."

  tags = ["http-server", "allow-health-checks"]

  labels = {
    environment = "dev"
  }

  instance_description = "Moshi media server"
  machine_type         = "e2-micro"
  can_ip_forward       = false

  metadata_startup_script = "/home/moshi/entrypoint_as_moshi.sh"

  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
  }

  disk {
    source_image = "moshi-3/moshi-srv"
    auto_delete  = true
    boot         = true
  }

  network_interface {
    network = "default"
  }

  service_account {
    # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
    email  = google_service_account.default.email
    scopes = ["cloud-platform"]
  }
}

resource "google_compute_health_check" "autohealing" {
  provider            = google-beta
  name                = "moshi-srv-hc"
  check_interval_sec  = 5
  timeout_sec         = 5
  healthy_threshold   = 2
  unhealthy_threshold = 10 # 50 seconds

  http_health_check {
    request_path = "/healthz"
    port         = "8080"
  }
}

# firewall rule to allow health checks
resource "google_compute_firewall" "allow-health-checks" {
  provider = google-beta
  name     = "moshi-srv-allow-health-checks"
  network  = "default"

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  source_ranges = [
    "130.211.0.0/22",
    "35.191.0.0/16"
  ]

}

resource "google_compute_instance_group_manager" "default" {
  // https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_instance_group_manager
  // https://cloud.google.com/compute/docs/instance-groups
  provider    = google-beta
  name        = "moshi-srv-igm"
  description = "This instance group is used to create Moshi media server instances."

  base_instance_name = "moshi-srv"
  zone               = "us-central1-c"
  version {
    instance_template = google_compute_instance_template.default.self_link
  }

  target_size = 1

  named_port {
    name = "http"
    port = 8080
  }

  auto_healing_policies {
    health_check      = google_compute_health_check.autohealing.id
    initial_delay_sec = 300
  }
}

resource "google_compute_security_policy" "default" {
  # https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_security_policy
  provider    = google-beta
  name        = "moshi-srv-sp"
  description = "This security policy is used to protect the Moshi media server load balancer."
  rule {
    action   = "allow"
    priority = "2147483647"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "default rule"
  }
  rule {
    action   = "rate_based_ban"
    priority = "1000"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "rate limit"
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      rate_limit_threshold {
        count        = 60
        interval_sec = 60
      }
      ban_duration_sec = 60
    }
  }
}

resource "google_compute_backend_service" "default" {
  # https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_backend_service
  provider    = google-beta
  name        = "moshi-srv-bs"
  description = "This backend service is used to route traffic to Moshi media server instances."

  protocol    = "HTTP"
  port_name   = "http"
  timeout_sec = 30

  load_balancing_scheme = "EXTERNAL"
  security_policy       = google_compute_security_policy.default.id

  backend {
    group = google_compute_instance_group_manager.default.instance_group
  }

  health_checks = [google_compute_health_check.autohealing.id]


}

resource "google_compute_url_map" "default" {
  # https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_url_map
  provider    = google-beta
  name        = "moshi-srv-um"
  description = "This URL map is used to route traffic to Moshi media server instances."

  default_service = google_compute_backend_service.default.self_link
}

resource "google_compute_global_address" "default" {
  # https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_global_address
  provider = google-beta
  # project     = "moshi-3"
  name        = "moshi-srv-ip"
  description = "This IP address is used by the Moshi media server load balancer."

  purpose      = "GLOBAL"
  address_type = "EXTERNAL"
}


# make an application load balancer with an HTTPS frontend 
# it must use the SSL cert created in ops/terraform/sslcert/main.tf
# it must use the URL map created in this file i.e. all traffic is routed to the backend service
resource "google_compute_global_forwarding_rule" "default" {
  # https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_global_forwarding_rule
  provider              = google-beta
  name                  = "moshi-srv-lb"
  description           = "This load balancer is used to route traffic to Moshi media server instances."
  target                = google_compute_target_https_proxy.default.self_link
  ip_address            = google_compute_global_address.default.address
  load_balancing_scheme = "EXTERNAL"
  port_range            = "443-443"

}

resource "google_compute_target_https_proxy" "default" {
  # https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_target_https_proxy
  provider    = google-beta
  name        = "moshi-srv-thp"
  description = "This target HTTP proxy is used to route traffic to Moshi media server instances."

  url_map          = google_compute_url_map.default.self_link
  ssl_certificates = ["projects/moshi-3/global/sslCertificates/moshi-srv-ssl"]
}


output "moshi-srv-external-ip" {
  value = google_compute_global_address.default.address
}
