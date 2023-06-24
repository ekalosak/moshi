#!/bin/bash
echo "STARTING UP"
su -l eric
echo "AS ERIC, PATH=$PATH"
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
