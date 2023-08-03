#!/bin/bash
# This script creates a Python VM image for Moshi on GCP.

# 1. create a VM instance e2-micro named "python-vm" with debian 11
# 2. run the script ./install_py_vm.sh on the VM instance
# 3. create a VM image from the VM instance
# 4. tear down the VM instance, leaving the image

echo "👋 Creating Python VM image for Moshi..."

# Check if the instance exists, if so continue
create_instance() {
    echo "🔧 Creating instance python-vm..." && \
    gcloud compute instances create python-vm \
        --zone=us-central1-a \
        --machine-type=e2-micro \
        --image-project=debian-cloud \
        --image-family=debian-11 \
        --boot-disk-size=10GB \
        --boot-disk-type=pd-balanced \
        --boot-disk-device-name=python-vm \
        --metadata-from-file startup-script=install_py_vm.sh && \
    echo "✅ Instance python-vm created!" || \
    echo "🚫 Instance creation failed, please try again."
}

gcloud compute instances describe python-vm --zone=us-central1-a 2>/dev/null 1>/dev/null && \
    echo "✅ Instance python-vm already exists." || \
    create_instance