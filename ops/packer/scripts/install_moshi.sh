#!/bin/bash
su - moshi && \
  echo "👋 Installing Moshi..." && \
  export PYENV_ROOT="$HOME/.pyenv" && \
  export PATH="$PYENV_ROOT/bin:$PATH" && \
  eval "$(pyenv init -)" && \
  pyenv activate moshi && \
  yes | pip install \
    keyring \
    keyrings.google-artifactregistry-auth && \
  mkdir -p ~/.config/pip && \
  mv pip.conf ~/.config/pip/pip.conf && \
  keyring --list-backends && \
  yes | pip install \
    --extra-index-url https://us-central1-python.pkg.dev/moshi-3/moshi/simple \
    gunicorn moshi && \
  pyenv deactivate && \
  echo "from moshi.api.core import app" > main.py && \
  echo "✅ Moshi installed!"