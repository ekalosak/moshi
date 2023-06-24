#!/bin/bash
su -l eric
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
echo "STARTUP"
echo "AS ERIC, PATH=$PATH"
echo "PYENV: $(command -v pyenv)"
eval "$(pyenv init -)" && \
eval "$(pyenv virtualenv-init -)" && \
pyenv activate moshi && \
pip install --upgrade moshi \
LOGURU_LEVEL=DEBUG \
MOSHICONNECTIONTIMEOUT=30 \
gunicorn main:app_factory \
  --bind :8080 \
  --workers 1 \
  --threads 1 \
  --timeout 5 \
  --worker-class aiohttp.GunicornWebWorker
