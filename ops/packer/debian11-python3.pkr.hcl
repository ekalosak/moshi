packer {
  required_plugins {
    googlecompute = {
      version = ">= 1.1.1"
      source = "github.com/hashicorp/googlecompute"
    }
  }
}

variable "project_id" {
  type    = string
  description = "The ID of your Google Cloud Platform project."
}

variable "ssh_username" {
  type    = string
  default = "devops"
  description = "The username for SSH access to the image."
}

variable "zone" {
  type    = string
  default = "us-central1-c"
  description = "The zone to create the image in."
}

variable "machine_type" {
  type    = string
  default = "e2-micro"
  description = "The machine type to create the image with."
}

locals {
  image_family = "python3"
}

source "googlecompute" "debian11python3" {
  project_id      = var.project_id
  zone            = var.zone
  machine_type    = var.machine_type
  ssh_username    = var.ssh_username
  source_image_family = "debian-11"
}

build {
  sources = [
    "source.googlecompute.debian11python3"
  ]

  provisioner "shell" {
    script = "scripts/install_python3.sh"
  }

}
