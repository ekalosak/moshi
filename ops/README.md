# Architecture
Packer bakes the VM images.
Terraform spins up the infra.
Python packages are stored on GCP Artifact Repository.
Builds are triggered by merges to main in GitHub.
Dev uses the latest VM image from the `moshi-srv` family.

The only IaC that's not in this `ops/` directory are the GitHub Actions in `./github/workflows` and the `Makefile`.

# Runbook

## First time on a brand new GCP project
Most of the IaC has hardcoded parameters so the values are tracked by version control. Currently, their values represent those used in the latest live version of Moshi. As such, you must examine and modify these scripts' constants to use them for a new project instance.
1. Run `./scripts/new_project_setup.sh` to setup billing and enable base set of GCP APIs.
1. Run `terraform apply pypi` to set up the PyPi repo in the GCP Artifact Repo. This also creates the service account require for baking the moshi-srv VM.
1. Run `packer build debian11-python3.pkr.hcl` to build the Python3 base VM.
1. Run `terraform apply github` and `./scripts/get_access_token_for_gha.sh`; put the secret in GitHub. This lets GH Actions push Python code to GCP.
1. Run `make publish` to build and push a version of moshi-server to GCP's artifact repo.
1. Run `./scripts/get_gcp_pypi_config.sh` to get the PyPi configuration artifacts.
1. Run `packer build moshi-server.pkr.hcl` to build the image. You will get a 401 if you don't put in the Service Account from `terraform apply pypi`.

### Manual steps
1. After running the `terraform apply` for the `storage/` components, run `gcloud storage cp artifacts/entrypoint.sh gs://moshi-<STORAGE_NAME>/entrypoint.sh` using the output from that tf apply command.
1. After running the `terraform apply` for GitHub components, retrieve the PROVIDER_NAME and SA_EMAIL; add these as secrets for the GH repo. [GCP OICD docs](https://github.com/terraform-google-modules/terraform-google-github-actions-runners/tree/master/modules/gh-oidc)

#### Firebase
1. Initialize a Firestore database in the console (I used multi-region nam5)
1. Activate FB Auth.
1. Update DNS records with custom domain.

## PyPi
To be able to publish to GCP Artifact Repo's PyPi, do this:
- `make auth-install`
- ```
gcloud artifacts print-settings python \
    --project=moshi-3 \
    --repository=pypi \
    --location=us-central1
```

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
