Moshi 3 (project ID: moshi-3) has been set up using as much declarative infrastructure as code (IaC) as possible.
That said, according to the [Terraform docs](https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/google-cloud-platform-build), some imperative setup is required.

This imperative new project setup is handled by `ops/new_project_setup.sh`.

Then, declarative infrastructure is applied using Terraform:
```sh
brew install terraform
terraform init
terraform fmt
terraform validate
```
What that command block does:
- init: download provider plugins
- fmt: format the .tf files
- validate: check they are valid .tf