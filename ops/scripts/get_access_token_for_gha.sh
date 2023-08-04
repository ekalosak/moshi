#!/bin/bash

service_account_name=artifact-writer
project_id=moshi-3
iam=$service_account_name@$project_id.iam.gserviceaccount.com

echo "🔧 Creating access token for service account $iam..."
echo "✋ Is this correct? (y/n)" && read confirm && \
    if [ "$confirm" != "y" ]; then echo "👋 Bye!"; exit 1; fi

gcloud iam service-accounts describe $iam 2>/dev/null 1>/dev/null && \
    echo "✅ Service account $service_account_name already exists." || \
    { echo "🚫 Service account $service_account_name does not exist, please create it first. See ops/terraform/github." ; exit 1; }

gcloud iam service-accounts keys create gha.json --iam-account $iam && \
    echo "✅ Access token created!" || \
    { echo "🚫 Access token creation failed, please try again." ; exit 1; }