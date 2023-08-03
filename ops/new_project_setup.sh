#!/bin/bash
# This script is used to setup a new GCP project for Moshi

echo "👋 Setting up new GCP project for Moshi..." 

# Check if gcloud is installed
command -v gcloud >/dev/null 2>&1 && \
    echo "✅ gcloud cli installed.!"  || \
    { echo >&2 "🚫 gcloud is not installed, please install it first." ; exit 1; }

# Check if gcloud is authenticated
gcloud_auth() {
    # If not authenticated, authenticate
    echo "🔑 Please authenticate with your GCP account, your browser will open..." && \
    gcloud auth login && \
    echo "✅ Authentication successful." || \
    { echo "🚫 Authentication failed, please try again." ; exit 1; }
}
gcloud auth list | grep -q "ACTIVE" && \
    echo "✅ Already authenticated." || \
    gcloud_auth

# Create new project
echo "👶 Enter the project name: " && read project_name
project_already_exists=false
gcloud projects describe $project_name && \
    { echo "✋ Project $project_name already exists, do you want to continue? (y/n)" && read confirm && \
        if [ "$confirm" != "y" ]; then echo "👋 Bye!"; exit 1; else project_already_exists=true; fi; } || \
    echo "✅ Project name $project_name is available!"
echo "🔧 Creating project $project_name..."
if [ "$project_already_exists" = false ]; then
    gcloud projects create $project_name --name=$project_name --set-as-default && \
        echo "✅ Project $project_name created!" || \
        { echo "🚫 Project creation failed, please try again." ; exit 1; }
fi

# Enable billing
echo "🔧 Enabling billing for project $project_name..."
gcloud beta billing projects link $project_name --billing-account=$(gcloud beta billing accounts list | grep -Eo '([0-9]{3}-){2}[0-9]{3}-[0-9]{3}') && \
    echo "✅ Billing enabled!" || \
    { echo "🚫 Billing enabling failed, please try again." ; exit 1; }