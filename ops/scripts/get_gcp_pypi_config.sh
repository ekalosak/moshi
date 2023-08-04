#!/bin/bash
# This script gets the configuration required for the GCP VM to access the GCP Artifact Repo's PyPi.

echo "👋 Getting GCP PyPi configuration..."
echo "👉 Please enter the following information:"
echo "🌩 GCP project name (e.g. moshi-3): " && read GOOGLE_CLOUD_PROJECT
echo "🌩 GCP PyPi name (e.g. moshi): " && read GOOGLE_CLOUD_PYPI_NAME
echo "🌩 GCP location (e.g. us-central1): " && read GOOGLE_CLOUD_LOCATION

echo "🔧 Getting GCP PyPi configuration..."
gcloud artifacts print-settings python --project=$GOOGLE_CLOUD_PROJECT \
    --repository=$GOOGLE_CLOUD_PYPI_NAME \
    --location=$GOOGLE_CLOUD_LOCATION && \
    echo "✅ GCP PyPi configuration retrieved!" || \
    { echo "🚫 GCP PyPi configuration read failed, please try again." ; exit 1; }
echo "💪 Create the artifacts as indicated above."
