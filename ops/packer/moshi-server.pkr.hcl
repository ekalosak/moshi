variable "project_id" {
  type        = string
  default     = "moshi-3"
  description = "The ID of your Google Cloud Platform project."
}

variable "base_image" {
  type        = string
  default     = "debian11-python310-1691105852"
  description = "The name of the base image to use for the instance."
}

variable "ssh_username" {
  type        = string
  default     = "devops"
  description = "The username for SSH access to the image."
}

variable "zone" {
  type        = string
  default     = "us-central1-c"
  description = "The zone to build the image in, where the image will live."
}

variable "machine_type" {
  type        = string
  default     = "e2-micro"
  description = "The machine type to use for building the instance."
}

locals {
  image_family = "moshi-srv"
}

source "googlecompute" "moshi" {
  project_id   = var.project_id
  zone         = var.zone
  machine_type = var.machine_type
  ssh_username = var.ssh_username
  source_image = "${var.base_image}"
  disk_size    = 10
  image_name   = "moshi-srv-{{timestamp}}"
}

build {
  sources = [
    "source.googlecompute.moshi"
  ]

  provisioner "shell" {
    script = "scripts/install_moshi.sh"
  }
}