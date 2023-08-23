// This Terraform file creates the resources required to run the Moshi media server.
//
// Sources:
// - https://cloud.google.com/load-balancing/docs/network/setting-up-network-backend-service
// - https://cloud.google.com/load-balancing/docs/network/udp-with-network-load-balancing

provider "google-beta" {
  project = "moshi-3"
  zone    = "us-central1-c"
}

// NETWORK RESOURCES
// Including ALB, NAT, and firewall rules

resource "google_compute_network" "default" {
  name                    = "moshi-srv-network"
  provider                = google-beta
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "default" {
  name                     = "moshi-srv-subnetwork"
  provider                 = google-beta
  ip_cidr_range            = "10.1.2.0/24"
  network                  = google_compute_network.default.self_link
  region                   = "us-central1"
  private_ip_google_access = true
}

resource "google_compute_global_forwarding_rule" "default" {
  # https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_global_forwarding_rule
  provider              = google-beta
  name                  = "moshi-srv-fwd"
  description           = "This forwarding rule is used to route HTTPS traffic to Moshi media server instances."
  target                = google_compute_target_https_proxy.default.self_link
  ip_address            = "34.110.228.236"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  port_range            = "443"
  labels = {
    environment = "dev"
  }

}

resource "google_compute_target_https_proxy" "default" {
  # https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_target_https_proxy
  # https://cloud.google.com/load-balancing/docs/https#target-proxies
  provider    = google-beta
  name        = "moshi-srv-thp"
  description = "This is used to route traffic to Moshi media server instances."

  url_map          = google_compute_url_map.default.self_link
  ssl_certificates = ["projects/moshi-3/global/sslCertificates/moshi-ssl-cert"]
}


resource "google_compute_firewall" "allow-health-checks" {
  provider = google-beta
  name     = "moshi-srv-allow-health-checks"
  network  = google_compute_network.default.self_link

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  source_ranges = [
    "130.211.0.0/22",
    "35.191.0.0/16"
  ]
}

// allow UDP and TCP from anyone to the templated instances
resource "google_compute_firewall" "allow-webrtc" {
  provider = google-beta
  name     = "moshi-srv-allow-webrtc"
  network  = google_compute_network.default.self_link

  allow {
    protocol = "udp"
    ports    = ["3478", "5349", "30000-65535"]
  }

  allow {
    protocol = "tcp"
    ports    = ["3478", "5349", "30000-65535"]
  }

  target_tags   = ["allow-webrtc"]
  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_url_map" "default" {
  # https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_url_map
  project     = "moshi-3"
  name        = "moshi-srv-um"
  description = "This URL map is used to route call traffic to Moshi media server instances."

  default_url_redirect {
    host_redirect          = "chatmoshi.com"
    https_redirect         = true
    strip_query            = true
    redirect_response_code = "FOUND"
  }
  host_rule {
    hosts        = ["dev.chatmoshi.com"]
    path_matcher = "dev-api"
  }
  host_rule {
    hosts        = ["chatmoshi.com", "www.chatmoshi.com"]
    path_matcher = "public-website"
  }
  path_matcher {
    name = "public-website"
    default_url_redirect {
      https_redirect = true
      host_redirect  = "chatmoshi.com"
      path_redirect  = "/"
      strip_query    = true
    }
    path_rule {
      paths   = ["*"]
      service = "projects/moshi-3/global/backendBuckets/moshi-web-bb"
      route_action {
        cors_policy {
          allow_credentials = false
          allow_origins     = ["https://chatmoshi.com", "https://www.chatmoshi.com"]
          allow_methods     = ["GET", "OPTIONS"]
          allow_headers     = ["Content-Type"]
          disabled          = false
        }
      }
    }
  }
  path_matcher {
    name = "dev-api"
    default_url_redirect {
      https_redirect = true
      host_redirect  = "dev.chatmoshi.com"
      path_redirect  = "/"
      strip_query    = true
    }
    path_rule {
      paths   = ["/", "/healthz", "/version", "/call/*"]
      service = google_compute_backend_service.default.self_link
      route_action {
        cors_policy {
          allow_credentials = true
          allow_origins     = ["https://dev.chatmoshi.com"]
          allow_methods     = ["GET", "POST", "OPTIONS"]
          allow_headers     = ["Content-Type", "Authorization"]
          disabled          = false
        }
      }
    }
  }
}

// SERVICE ACCOUNT
resource "google_project_iam_member" "logging-write" {
  project = "moshi-3"
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.default.email}"
}

resource "google_project_iam_member" "secrets-read" {
  project = "moshi-3"
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.default.email}"
}

resource "google_project_iam_member" "storage-read" {
  project = "moshi-3"
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.default.email}"
}

// Read from and write to Firestore
resource "google_project_iam_member" "firestore-read" {
  project = "moshi-3"
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.default.email}"
}

// Check user's auth tokens via Firebase Auth
resource "google_project_iam_member" "firebase-auth-read" {
  project = "moshi-3"
  role    = "roles/firebaseauth.viewer"
  member  = "serviceAccount:${google_service_account.default.email}"
}

resource "google_service_account" "default" {
  // https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/service_account
  provider     = google-beta
  account_id   = "moshi-srv-sa"
  display_name = "Service Account for the Moshi media server's VMs."
  // https://cloud.google.com/iam/docs/understanding-roles#compute-engine-roles
}



// VM RESOURCES
resource "google_compute_instance_template" "default" {
  // https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_instance_template
  provider    = google-beta
  name        = "moshi-srv-template"
  description = "This template is used to create Moshi media server instances."

  tags = ["allow-health-checks", "allow-webrtc"]

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
    network    = google_compute_network.default.self_link
    subnetwork = google_compute_subnetwork.default.self_link
    access_config {
      // Ephemeral IP provided when this block is null.
      // https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_instance_template#nested_access_config
      // https://cloud.google.com/compute/docs/reference/rest/v1/instanceTemplates
    }
  }

  service_account {
    // Service account to attach to the instance.
    // Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
    email  = google_service_account.default.email
    scopes = ["cloud-platform"]
  }
}

resource "google_compute_health_check" "autohealing" {
  # https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_health_check
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

  load_balancing_scheme = "EXTERNAL_MANAGED"
  security_policy       = google_compute_security_policy.default.id

  backend {
    group = google_compute_instance_group_manager.default.instance_group
  }

  health_checks = [google_compute_health_check.autohealing.id]


}
