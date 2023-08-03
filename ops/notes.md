# Architecture
Packer bakes the VM images.
Terraform spins up the infra.
They are run on Google Cloud Build.
Builds are triggered by merges to main in GitHub.

# Packer
1. `packer init` downloads the GCP plugin
2. `packer validate` checks the .pkr.hcl

## Init
`packer init .` is all you need.

## Validate
```sh
packer validate \
    -var="project_id=moshi-3" \
    debian11-python3.pkr.hcl
```

# Miscelanea
### num workers in entrypoint.sh
gunicorn workers 3 because wrk=2xCore+1
https://docs.gunicorn.org/en/stable/design.html#how-many-workers
