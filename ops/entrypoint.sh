#!/bin/bash
eval "$(pyenv init -)" && \
pyenv activate moshi && \
LOGURU_LEVEL=TRACE \
MOSHICONNECTIONTIMEOUT=30 \
gunicorn main:app_factory \
  --bind :8080 \
  --workers 1 \
  --threads 1 \
  --timeout 5 \
  --worker-class aiohttp.GunicornWebWorker
