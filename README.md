# 🧑💬🤖 moshi
Moshi is a spoken language tutor.

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
pytest -m 'not openai and not gcloud and not slow'
```

## Run on the local App Engine
```sh
set -x GOOGLE_CLOUD_PROJECT moshi-002
set -x CLOUD_SDK_ROOT /Users/eric/bin/google-cloud-sdk

python3 $CLOUD_SDK_ROOT/bin/dev_appserver.py \
--port=8080 \
--host=localhost \
    --runtime_python_path="python3=/Users/eric/.pyenv/shims/python3,python27=/Users/eric/.pyenv/shims/python2" \
    app.yaml
```
Computer go brrr, then `localhost:8080`.

# Usage

To start the web server:
```bash
python moshi/main.py
```

# Deployment
`cd app && gcloud app deploy`
