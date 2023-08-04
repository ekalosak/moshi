# Architecture
Packer bakes the VM images.
Terraform spins up the infra.
They are run on Google Cloud Build.
Builds are triggered by merges to main in GitHub.
Python artifacts are stored on GCP Artifact Repository.

The only IaC that's not in this `ops/` directory are the GitHub Actions in `./github/workflows` and the `Makefile`.

# Runbook

## First time on a brand new GCP project
1. Run `./scripts/new_project_setup.sh` to setup billing and enable base set of GCP APIs.
2. Run `./scripts/create_python_repo.sh` to create the GCP-hosted PyPi.
3. Modify and run `packer build debian11-python3.pkr.hcl` to build the Python3 base VM.

## CD


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
packer validate debian11-python3.pkr.hcl
```

## Build

### Base image
```sh
packer build debian11-python3.pkr.hcl
```
