# This TF creates the GCP Cloud Storage bucket that will be used to store the Moshi media server's data.
# Primarily, at the moment, this is the Moshi media server's entrypoint.sh script.
provider "google-beta" {
  project = "moshi-3"
}

resource "google_storage_bucket" "moshi-srv" {
  provider = google-beta

  # NOTE: name is globally unique and lowercase so I do the following to generate a random string:
  #     `uuidgen | cut -f 1 -d '-'| tr '[:upper:]' '[:lower:]'`
  name          = "moshi-5aee1af5"
  location      = "us-central1"
  storage_class = "STANDARD"
#   force_destroy = true  # if true, non-empty buckets can be destroyed
}

output "moshi-srv-bucket-name" {
  value = google_storage_bucket.moshi-srv.name
}