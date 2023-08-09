#!/bin/bash
su - moshi && \
  echo "👋 $(whoami)" && \
  echo "📜 PATH: $PATH" && \
  echo "📜 PYENV: $(command -v pyenv)" && \
  echo "📜 PYTHON3: $(command -v python3)" && \
  echo "📜 GUNICORN: $(command -v gunicorn)" && \
  echo "🔧 Running Moshi..." && \
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