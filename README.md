# 🧑💬🤖 moshi
Moshi is a spoken language tutor.

# Summary
Moshi is deployed as an HTTP server exposed to end users over the public internet. It provides an HTML/Javascript interface used to establish audio connections over WebRTC.

Code is un

# Build
Uses `setuptools` and `build` to package Python code.

Run this:
```
make build-install && make build
```

Files:
- Makefile
- pyproject.toml
- setup.cfg

## Push to gcloud PyPi
With the Google Cloud Artifact Registry set up (see notes/../GOOGLE_CLOUD.md for runbook):
```fish
gcloud auth login
set -x GOOGLE_CLOUD_PYPI_URL https://us-east1-python.pkg.dev/moshi-002/moshi-002-repo/
pip install twine keyring keyrings.google-artifactregistry-auth
keyring --list-backends
python3 -m twine upload \
    --repository-url $GOOGLE_CLOUD_PYPI_URL \
    "dist/*" \
    --verbose
```
^ hit enter through the usrnames
Source: https://cloud.google.com/artifact-registry/docs/python/authentication#keyring-setup
When u list-backends, look for GCloud. If u don't see, GLHF.

# Development

## Setup

Setup virtualenv and install project & its Python dependencies:
```bash
eval "$(pyenv init -)" && \
    eval "$(pyenv virtualenv-init -)" && \
    pyenv virtualenv 3.10-dev mm310 && \
    pyenv activate mm310 && \
    pip install --upgrade pip && \
    pip install -e .
```

For a development installation, use the `-e` flag:
```sh
mkdir build && \
    pip install -e .[dev,test]
```
Note that the `setup.cfg` puts the `.egg-info` into the local `./build` directory; you MUST create the `build` dir first.

## Docs
```
(cd moshi/ && python -m pydoc -b)
```

# Testing
Make sure you have the test dependencies installed:
```bash
pip install -e .[test]
```

Test using pytest:
```bash
pytest -m 'not openai and not gcloud and not slow and not frontend'
```

## Frontend test
https://selenium-python.readthedocs.io/installation.html#introduction
`brew install geckodriver`

# Usage

To start the web server:
```bash
MOSHINOSECURITY=1 python app/main.py --port 8080
```

# Deployment
The instance groups will pull the latest `moshi` python package available on the repo.
- Entrypoint is in Cloudstore, see ops/entrypoint.sh and notes/runbooks
- Python package is in gcloud repo, see Makefile and notes/runbooks

So you just do `make publish` and cycle the instance group to deploy latest to prod.
