# Architecture
Packer bakes the VM images.
Terraform spins up the infra.
They are run on Google Cloud Build.
Builds are triggered by merges to main in GitHub.
Python artifacts are stored on GCP Artifact Repository.

# Runbook

## First time on a brand new GCP project
1. Run `./scripts/new_project_setup.sh` to setup billing and enable base set of GCP APIs.
2. Run `./scripts/create_python_repo.sh` to create the GCP-hosted PyPi.
3. Run `packer build -var="project_id=MY_PROJECT" debian11-python3.pkr.hcl` to build the Python3 base VM.
4. Run `make publish` from the project root to build and publish moshi-srv.

# Packer
Packer creates VM images. Basically Docker for VMs across cloud providers.

## Initialize
The `init` command pulls HashiCorp's GCP "googlecompute" plugin.
```sh
packer init .
```

## Format
Easy as:
```sh
packer fmt .
```

## Validate

### Base image
```sh
packer validate \
    -var="project_id=moshi-3" \
    debian11-python3.pkr.hcl
```

## Build

### Base image
```sh
packer build \
    -var="project_id=moshi-3" \
    debian11-python3.pkr.hcl
```