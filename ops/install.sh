#!/bin/bash
pyenv update && \
  pyenv install -v 3.10 && \
  pyenv virtualenv 3.10 moshi && \
  pyenv activate moshi && \
  yes | pip install --upgrade pip && \
  yes | pip install \
    keyring \
    keyrings.google-artifactregistry-auth && \
  yes | pip install \
    --extra-index-url https://us-east1-python.pkg.dev/moshi-002/moshi-002-repo/simple \
    gunicorn moshi && \
  cat <<EOT >> main.py
from moshi.server import make_app

async def app_factory():
    return await make_app()
EOT
