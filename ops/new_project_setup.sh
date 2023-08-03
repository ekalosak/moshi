#!/bin/bash
# This script is used to setup a new GCP project for Moshi.
# It will check and/or install Terraform prerequisites.

echo "👋 Setting up new GCP project for Moshi..." 

# Check if gcloud is installed
echo "🔧 Checking if gcloud cli is installed..."
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
gcloud auth list 2>/dev/null | grep -q "ACTIVE" && \
    echo "✅ Already authenticated." || \
    gcloud_auth

# Check if billing is enabled
# NOTE this doesn't let you pick which billing account to use, just that there is one.
echo "🔧 Checking if billing is enabled..."
gcloud beta billing accounts list | grep -q "True" && \
    echo "✅ Billing is enabled." || \
    { echo "🚫 Billing is not enabled, please enable it first." ; exit 1; }

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

# If there's more than one billing account, barf
echo "🔧 Checking if there's only one billing account..."
gcloud beta billing accounts list --format json | jq -r '. | length' | grep -q "1" && \
    echo "✅ Only one billing account found." || \
    { echo "🚫 More than one billing account found, please fix this first." ; exit 1; }

# Enable billing
billing_account=$(gcloud beta billing accounts list --format json | jq -r '.[0].name')
echo "🔧 Enabling billing for project $project_name using $billing_account..."
gcloud beta billing projects link $project_name --billing-account=$billing_account && \
    echo "✅ Billing enabled!" || \
    { echo "🚫 Billing enabling failed, please try again." ; exit 1; }

