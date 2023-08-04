#!/bin/bash
yes | pip install \
    keyring \
    keyrings.google-artifactregistry-auth && \
  yes | pip install \
    --extra-index-url https://us-central1-python.pkg.dev/moshi-3/moshi/simple \
    gunicorn moshi && \
  echo "from moshi.api.core import app" > main.py && \
  echo "✅ Moshi installed!"