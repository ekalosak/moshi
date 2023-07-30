#!/bin/bash
su - eric -c '
  export PYENV_ROOT="$HOME/.pyenv"
  export PATH="$PYENV_ROOT/bin:$PATH"
  echo "STARTUP ✅"
  echo "WHOAMI: $(whoami)"
  echo "PATH: $PATH"
  echo "PYENV: $(command -v pyenv)"
  eval "$(pyenv init -)" && \
  eval "$(pyenv virtualenv-init -)" && \
  pyenv activate moshi && \
  pip install \
    --upgrade \
    --extra-index-url https://us-east1-python.pkg.dev/moshi-002/moshi-002-repo/simple \
    moshi==23.7.0 && \
  LOGURU_LEVEL=DEBUG \
  MOSHICONNECTIONTIMEOUT=30 \
  MOSHILOFILE=0 \
  MOSHILOGSTDOUT=0 \
  MOSHILOGCLOUD=1 \
  gunicorn main:app \
    --bind :8080 \
    --workers 3 \
    --threads 4 \
    --timeout 20 \
    --worker-class uvicorn.workers.UvicornWorker
'
