# Startup script bucket
1. gcloud storage buckets create gs://startup-scripts-63feba6b
    - Buckets are GLOBALLY unique, you read it right, across evey GCP user
2. gcloud storage cp ops/entrypoint.sh gs://startup-scripts-63feba6b/entrypoint.sh

