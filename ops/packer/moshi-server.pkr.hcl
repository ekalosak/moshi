locals {
  ssh_username = "packer"
}

source "googlecompute" "moshi" {
  project_id            = "moshi-3"
  zone                  = "us-central1-c"
  machine_type          = "e2-micro"
  ssh_username          = "${local.ssh_username}"
  source_image          = "debian11-python310-1691178818"
  disk_size             = 10
  image_name            = "moshi-srv-{{timestamp}}"
  image_family          = "moshi-srv"
  service_account_email = "artifact-reader@moshi-3.iam.gserviceaccount.com"
  scopes                = ["https://www.googleapis.com/auth/cloud-platform"]
}

build {
  sources = ["source.googlecompute.moshi"]

  provisioner "file" {
    source      = "scripts/install_moshi.sh"
    destination = "/home/${local.ssh_username}/install_moshi.sh"
  }

  provisioner "file" {
    source      = "artifacts/entrypoint.sh"
    destination = "/tmp/entrypoint.sh"
  }

  provisioner "shell" {
    inline = [
      "sudo chown moshi /tmp/entrypoint.sh",
      "sudo -u moshi ./install_moshi.sh"
    ]
  }
}