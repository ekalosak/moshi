#!/bin/bash
PYTHON_VERSION=3.10
echo "👋 Installing Moshi..."
echo "👉 whoami: $(whoami)"
echo "👉 shell: $SHELL"
export PYENV_ROOT="$HOME/.pyenv" && \
export PATH="$PYENV_ROOT/bin:$PATH" && \
echo "👉 PATH: $PATH" && \
echo "👉 PYENV_ROOT: $PYENV_ROOT" && \
eval "$(pyenv init -)" && \
echo "👉 pyenv: $(pyenv --version)" && \
echo "👉 which pyenv: $(which pyenv)" && \
echo "👉 pyenv versions:"
pyenv versions && \
pyenv activate moshi && \
echo "✅ Python virtual environment activated!" && \
echo "🔧 Installing keyring..." && \
yes | pip install --upgrade pip && \
yes | pip install \
  keyring \
  keyrings.google-artifactregistry-auth && \
echo "✅ Keyring installed!" && \
echo "👉 Keyrings:" && \
keyring --list-backends && \
echo "🔧 Configuring pip..." && \
mkdir -p ~/.config/pip && \
mv ~/pip.conf ~/.config/pip/pip.conf && \
echo "✅ Pip configured!" && \
echo "🔧 Installing moshi..." && \
yes | pip install \
  --extra-index-url https://us-central1-python.pkg.dev/moshi-3/moshi/simple \
  gunicorn moshi && \
pyenv deactivate && \
echo "from moshi.api.core import app" > main.py && \
echo "✅ Moshi installed!"