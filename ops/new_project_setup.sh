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
# Check if billing is enabled for the project, if not enable it
gcloud beta billing projects describe $project_name | grep -q "billingEnabled: true" && \
    echo "✅ Billing is already enabled for project $project_name." || \
    enable_billing

# Set the gcloud project to the new one.
gcloud config set project $project_name && \
    echo "✅ Project set to $project_name." || \
    { echo "🚫 Project setting failed, please try again." ; exit 1; }


# Enable the base set of APIs
# NOTE further API enablement is done in the Terraform code.
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
echo "✅ All required APIs are enabled!"

# Create a service account for Terraform
gcloud iam service-accounts list --project $project_name | grep -q "terraform" && \
    echo "✅ Service account terraform already exists." || \
    { echo "🔧 Creating service account terraform..." && \
        gcloud iam service-accounts create terraform --display-name "Terraform service account" --project $project_name && \
        echo "✅ Service account terraform created!" || \
        { echo "🚫 Service account creation failed, please try again." ; exit 1; } }
gcloud projects get-iam-policy $project_name --format json | jq -r '.bindings[] | select(.role == "roles/editor") | .members[]' | grep -q "terraform" && \
    echo "✅ Service account terraform already has the right permissions." || \
    { echo "🔧 Adding project editor permissions to service account terraform..." && \
        gcloud projects add-iam-policy-binding $project_name --member serviceAccount:terraform@$project_name.iam.gserviceaccount.com --role roles/editor && \
        echo "✅ Service account terraform has the right permissions!" || \
        { echo "🚫 Service account permissions adding failed, please try again." ; exit 1; } }
[ -f "terraform-key.json" ] && \
    echo "✅ Service account key already exists on the local machine." || \
    { echo "🔧 Downloading service account key..." && \
        gcloud iam service-accounts keys create terraform-key.json --iam-account terraform@$project_name.iam.gserviceaccount.com && \
        echo "✅ Service account key downloaded!" || \
        { echo "🚫 Service account key downloading failed, please try again." ; exit 1; } }