variable "project_id" {
  type        = string
  description = "The ID of your Google Cloud Platform project."
}

variable "base_image" {
  type        = string
  description = "The name of the base image to use for the instance."
}

variable "ssh_username" {
  type        = string
  default     = "devops"
  description = "The username for SSH access to the image."
}

locals {
  image_family = "moshi-srv"
}

source "googlecompute" "moshi" {
  project      = var.project_id
  zone         = var.zone
  machine_type = var.machine_type
  source_image = "projects/${var.project_id}/global/images/${var.base_image}"
  disk_size_gb = 10
  network      = "default"
}

build {
    sources = [
        "source.googlecompute.moshi"
    ]

    provisioner "shell" {
        script = "scripts/install_python3.sh"
    }
}