# 1. image template in us-central1 that uses the latest image from the "moshi-srv" image family
# 2. Instance group in us-central1 that uses the image template 
# 3. Load balancer (ALB) in us-central1 that routes traffic to the instance group
# 4. External IP address in us-central1 that is used by the load balancer
# 5. Health check in us-central1 that is used by the load balancer against the vm's /heathz endpoint

provider "google-beta" {
  project = "moshi-3"
}
  
resource "google_service_account" "default" {
  account_id   = "moshi-srv-sa"
  display_name = "Service Account for the Moshi media server."
}

resource "google_project_iam_member" "default" {
  project = "moshi-3"
  role    = "roles/compute.instanceAdmin"
  member  = "serviceAccount:${google_service_account.default.email}"
}

resource "google_compute_instance_template" "default" {
  // https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_instance_template
  name        = "moshi-srv-template"
  description = "This template is used to create Moshi media server instances."

  tags = ["server", "moshi-srv", "moshi", "media-server"]

  labels = {
    environment = "dev"
  }

  instance_description = "Moshi media server"
  machine_type         = "e2-micro"
  can_ip_forward       = false

  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
  }

  disk {
    source_image      = "moshi-3/moshi-srv"
    auto_delete       = true
    boot              = true
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
  name                = "autohealing-health-check"
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
  name        = "moshi-srv-igm"
  description = "This instance group is used to create Moshi media server instances."

  base_instance_name = "moshi-srv"
  zone               = "us-central1-c"
  version {
    instance_template  = google_compute_instance_template.default.self_link
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

## load balancer ALB
resource "google_compute_backend_service" "default" {
  # https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_backend_service
  name        = "moshi-srv-bs"
  description = "This backend service is used to route traffic to Moshi media server instances."

  protocol = "HTTP"
  port_name = "http"
  timeout_sec = 10

  backend {
    group = google_compute_instance_group_manager.default.self_link
  }

  health_checks = [google_compute_health_check.autohealing.id]
}

resource "google_compute_url_map" "default" {
  # https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_url_map
  name        = "moshi-srv-um"
  description = "This URL map is used to route traffic to Moshi media server instances."

  default_service = google_compute_backend_service.default.self_link
}