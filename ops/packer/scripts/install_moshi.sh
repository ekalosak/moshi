#!/bin/bash
export PYENV_ROOT="$HOME/.pyenv" && \
  export PATH="$PYENV_ROOT/bin:$PATH" && \
  eval "$(pyenv init -)" && \
  pyenv activate moshi && \
  yes | pip install \
    keyring \
    keyrings.google-artifactregistry-auth && \
  yes | pip install \
    --extra-index-url https://us-central1-python.pkg.dev/moshi-3/moshi/simple \
    gunicorn moshi && \
  pyenv deactivate && \
  echo "from moshi.api.core import app" > main.py && \
  echo "✅ Moshi installed!"