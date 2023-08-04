variable "project_id" {
  type        = string
  default     = "moshi-3"
  description = "The ID of your Google Cloud Platform project."
}

variable "base_image" {
  type        = string
  default     = "debian11-python310-1691178818"
  description = "The name of the base image to use for the instance."
}

variable "ssh_username" {
  type        = string
  default     = "packer"
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

variable "service_account" {
  type        = string
  default     = "artifact-reader"
  description = "The name of the GCP Service Account to use for building the image."
}

locals {
  image_family = "moshi-srv"
}

source "googlecompute" "moshi" {
  project_id            = var.project_id
  zone                  = var.zone
  machine_type          = var.machine_type
  ssh_username          = var.ssh_username
  source_image          = "${var.base_image}"
  disk_size             = 10
  image_name            = "moshi-srv-{{timestamp}}"
  image_family          = local.image_family
  service_account_email = "${var.service_account}@${var.project_id}.iam.gserviceaccount.com"
}

build {
  sources = ["source.googlecompute.moshi"]

  provisioner "file" {
    source      = "artifacts/pypirc"
    destination = "/home/${var.ssh_username}/.pypirc"
  }


  provisioner "file" {
    source      = "artifacts/pip.conf"
    destination = "/home/${var.ssh_username}/pip.conf"
  }

  provisioner "file" {
    source      = "scripts/install_moshi.sh"
    destination = "/home/${var.ssh_username}/install_moshi.sh"
  }

  provisioner "shell" {
    inline = [
      "sudo mv .pypirc /home/moshi/",
      "sudo mv pip.conf /home/moshi/",
      "sudo -u moshi ./install_moshi.sh"
    ]
  }
}