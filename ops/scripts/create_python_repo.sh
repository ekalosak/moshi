#!/bin/bash
# This script is used to setup a new GCP Artifacts Repository for Moshi.

echo "👋 Setting up new GCP Artifacts Repository for Moshi..."

# Configure
echo "👶 Enter the region (default: us-central1): " && read REGION
echo "👶 Enter the repo name (default: moshi): " && read REPO
if [ -z "$REGION" ]; then REGION=us-central1; fi
if [ -z "$REPO" ]; then REPO=moshi; fi

# Precheck
gcloud auth list 2>/dev/null | grep "ACTIVE" >/dev/null || \
    { echo "🚫 Not authenticated, please run gcloud auth login first." ; exit 1; }
PROJECT_ID=$(gcloud config get-value project)
echo "✋ Project ID is $PROJECT_ID, is this correct? (y/n)" && read confirm && \
    if [ "$confirm" != "y" ]; then echo "👋 Bye!"; exit 1; fi

# Enable the Artifact Registry API
echo "🔧 Enabling Artifact Registry API..."
gcloud services enable artifactregistry.googleapis.com && \
    echo "✅ Artifact Registry API enabled!" || \
    { echo "🚫 Artifact Registry API enabling failed, please try again." ; exit 1; }

# Create new repository
gcloud artifacts repositories create $REPO \
    --repository-format=python \
    --location=$REGION \
    --description="Moshi server" && \
    echo "✅ Repository $REPO created!" || \
    { echo "🚫 Repository creation failed, please try again." ; exit 1; }