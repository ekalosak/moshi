# Architecture
Packer bakes the VM images.
Terraform spins up the infra.
They are run on Google Cloud Build.
Builds are triggered by merges to main in GitHub.
Python artifacts are stored on GCP Artifact Repository.

The only IaC that's not in this `ops/` directory are the GitHub Actions in `./github/workflows` and the `Makefile`.

# Runbook

## First time on a brand new GCP project
Most of the IaC has hardcoded parameters so the values are tracked by version control. Currently, their values represent those used in the latest live version of Moshi. As such, you must examine and modify these scripts' constants to use them for a new project instance.
1. Run `./scripts/new_project_setup.sh` to setup billing and enable base set of GCP APIs, along with an Artifact Repo. for the Python package.
2. Run `./scripts/create_python_repo.sh` to create the GCP-hosted PyPi.
3. Run `packer build debian11-python3.pkr.hcl` to build the Python3 base VM.
4. Run `terraform apply github` and `./scripts/get_access_token_for_gha.sh`; put the secret in GitHub. This lets GH Actions push Python code to GCP.
5. Run `terraform apply packer`; this creates the service account used to read 
6. Run `make publish` to build and push a version of moshi-server to GCP's artifact repo.
7. Run `./scripts/get_gcp_pypi_config.sh` to get the PyPi configuration artifacts.
7. Run `packer build moshi-server.pkr.hcl` to build the image. You will get a 401 if you don't put in the Service Account from `terraform apply packer`.

### Manual steps
1. After running the `terraform apply` for GitHub components, retrieve the PROVIDER_NAME and SA_EMAIL; add these as secrets for the GH repo. [GCP OICD docs](https://github.com/terraform-google-modules/terraform-google-github-actions-runners/tree/master/modules/gh-oidc)

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
