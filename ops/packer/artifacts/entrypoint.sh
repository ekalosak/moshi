#!/bin/bash
echo "🏁 STARTING ENTRYPOINT.SH 🏁"
export PYENV_ROOT="$HOME/.pyenv" && \
export PATH="$PYENV_ROOT/bin:$PATH" && \
echo "👋 I am: $(whoami)" && \
echo "👉 PATH: $PATH" && \
eval "$(pyenv init -)" && \
echo "👉 PYENV: $(pyenv --version)" && \
echo "🔧 Activating Python virtual environment..." && \
pyenv activate moshi && \
echo "✅ Python virtual environment activated!" && \
echo "👉 PYTHON3: $(python3 -V)" && \
echo "👉 GUNICORN: $(gunicorn --version)" && \
echo "👉 MOSHI: $(python3 -c 'import moshi; print(moshi.__version__)')" && \
echo "🔧 Running Moshi..." && \
GOOGLE_PROJECT_ID=moshi-3 \
MLOGLEVEL=TRACE \
MOSHICONNECTIONTIMEOUT=30 \
MOSHILOFILE=0 \
MOSHILOGSTDOUT=0 \
MOSHILOGCLOUD=1 \
gunicorn main:app \
  --bind :8080 \
  --workers 1 \
  --threads 1 \
  --timeout 30 \
  --worker-class uvicorn.workers.UvicornWorker