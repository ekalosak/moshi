#!/bin/bash
# This script is used to setup a new GCP project for Moshi.
# It will check and/or install Terraform prerequisites.

echo "👋 Setting up new GCP project for Moshi..." 

# Check if gcloud is installed
echo "🔧 Checking if gcloud cli is installed..."
command -v gcloud >/dev/null 2>&1 && \
    echo "✅ gcloud cli installed."  || \
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


# Create new project
echo "👶 Enter the project name: " && read project_name
project_already_exists=false
gcloud projects describe $project_name && \
    { echo "✋ Project $project_name already exists, do you want to continue? (y/n)" && read confirm && \
        if [ "$confirm" != "y" ]; then echo "👋 Bye!"; exit 1; else project_already_exists=true; fi; } || \
    echo "✅ Project name $project_name is available!"
if [ "$project_already_exists" = false ]; then
    echo "🔧 Creating project $project_name..." && \
    gcloud projects create $project_name --name=$project_name --set-as-default && \
        echo "✅ Project $project_name created!" || \
        { echo "🚫 Project creation failed, please try again." ; exit 1; }
fi

# Check if billing is enabled for the project
enable_billing() {
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

}
gcloud beta billing projects describe $project_name | grep -q "billingEnabled: true" && \
    echo "✅ Billing is already enabled for project $project_name." || \
    enable_billing

# Enable APIs: compute engine, IAM
required_apis="compute.googleapis.com iam.googleapis.com"
echo "🔧 Checking if required APIs are enabled..."
for api in $required_apis; do
    echo "    🔧 Checking if $api is enabled..."
    gcloud services list --project $project_name | grep -q $api && \
        echo "    ✅ $api already enabled." || \
        { echo "    🔧 Enabling $api..." && \
            gcloud services enable $api --project $project_name && \
            echo "    ✅ $api enabled!" || \
            { echo "🚫 $api enabling failed, please try again." ; exit 1; } }
done

# Create a service account for Terraform:
# 1. Check if the service account already exists.
# 2. If not, create it.
# 3. If yes, check if it has the right permissions.
# 4. If not, add the right permissions: project editor.
# 5. Check if the service account key already exists on the local machine.
# 6. If not, download it.
gcloud iam service-accounts list --project $project_name | grep -q "terraform" && \
    echo "✅ Service account terraform already exists." || \
    { echo "🔧 Creating service account terraform..." && \
        gcloud iam service-accounts create terraform --display-name "Terraform service account" --project $project_name && \
        echo "✅ Service account terraform created!" || \
        { echo "🚫 Service account creation failed, please try again." ; exit 1; } }
