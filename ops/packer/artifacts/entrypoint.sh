#!/bin/bash
echo "🏁 STARTING ENTRYPOINT.SH 🏁"
# sudo -u moshi bash -c ' \
export PYENV_ROOT="$HOME/.pyenv" && \
export PATH="$PYENV_ROOT/bin:$PATH" && \
echo "👋 I am: $(whoami)" && \
echo "👉 PATH: $PATH" && \
eval "$(pyenv init -)" && \
echo "👉 PYENV: $(command -v pyenv)" && \
echo "🔧 Activating Python virtual environment..." && \
pyenv activate moshi && \
echo "✅ Python virtual environment activated!" && \
echo "👉 PYTHON3: $(command -v python3)" && \
echo "👉 GUNICORN: $(command -v gunicorn)" && \
echo "🔧 Running Moshi..." && \
GOOGLE_PROJECT_ID=moshi-3 \
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
# '