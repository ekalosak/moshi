#!/bin/bash
pyenv update && \
  pyenv install -v 3.10 && \
  pip install \
    --extra-index-url https://us-east1-python.pkg.dev/moshi-002/moshi-002-repo/simple \
    gunicorn moshi && \
  cat <<EOT >> main.py
from moshi.server import make_app

async def app_factory():
    return await make_app()
EOT
