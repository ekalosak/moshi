#!/bin/bash
echo "🏁 STARTING ENTRYPOINT.SH 🏁"
export PYENV_ROOT="$HOME/.pyenv" && \
export PATH="$PYENV_ROOT/bin:$PATH" && \
echo "👋 I am: $(whoami)" && \
echo "👉 PATH: $PATH" && \
eval "$(pyenv init -)" && \
echo "👉 PYENV: $(command -v pyenv)" && \
# echo "🔧 Activating Python virtual environment..." && \
# pyenv activate moshi && \
# echo "✅ Python virtual environment activated!" && \
echo "👉 PYTHON3: $(command -v python3)" && \
echo "👉 GUNICORN: $(command -v gunicorn)" && \
echo "🔧 Running Moshi..." && \
GOOGLE_PROJECT_ID=moshi-3 \
MLOGLEVEL=TRACE \
MOSHICONNECTIONTIMEOUT=30 \
MOSHILOFILE=0 \
MOSHILOGSTDOUT=1 \
MOSHILOGCLOUD=0 \
gunicorn main:app \
  --bind :8080 \
  --workers 1 \
  --threads 1 \
  --timeout 45 \
  --worker-class uvicorn.workers.UvicornWorker