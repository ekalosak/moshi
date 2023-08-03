# Install tooling
1. gcloud
2. `brew install terraform`
3. `brew install packer`

# New GCP project
Create a new GCP project, ensure billing is enabled, and enable the required APIs:
`ops/new_project_setup.sh`.

# Bake the VM images
Using Packer:
