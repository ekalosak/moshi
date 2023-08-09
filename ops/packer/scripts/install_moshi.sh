#!/bin/bash
PYTHON_VERSION=3.10
cd /home/moshi
cp /tmp/entrypoint.sh .
echo "👋 Installing Moshi..."
echo "👉 whoami: $(whoami)"
echo "👉 pwd: $(pwd)"
echo "👉 shell: $SHELL"
export PYENV_ROOT="$HOME/.pyenv" && \
export PATH="$PYENV_ROOT/bin:$PATH" && \
eval "$(pyenv init -)" && \
echo "👉 PATH: $PATH" && \
echo "👉 PYENV_ROOT: $PYENV_ROOT" && \
echo "👉 which pyenv: $(which pyenv)" && \
echo "👉 pyenv version: $(pyenv --version)" && \
echo "👉 pyenv versions:"
pyenv versions && \
pyenv activate moshi && \
echo "✅ Python virtual environment activated!" && \
echo "👉 pyenv versions:"
pyenv versions && \
echo "🔧 Installing keyring..." && \
yes | pip install --upgrade pip && \
yes | pip install \
  keyring \
  keyrings.google-artifactregistry-auth && \
echo "✅ Keyring installed!" && \
echo "👉 Keyrings:" && \
keyring --list-backends && \
echo "🔧 Installing moshi..." && \
pip install --extra-index-url https://us-central1-python.pkg.dev/moshi-3/pypi/simple moshi[server] && \
echo "from moshi.api.core import app" > main.py && \
echo "✅ Moshi installed!" && \
echo "👉 Moshi version: $(python3 -c 'import moshi; print(moshi.__version__)')" && \
pyenv deactivate