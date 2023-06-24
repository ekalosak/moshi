# CD
Because the startup script is gs://startup-scripts-63feba6b/entrypoint.sh
Just update the ops/entrypoint.sh and upload it, reset instances or wait for churn.
It updates to latest moshi in the GCP repo, so if you publish new version, wait for churn, it should auto-deploy to
prod.
