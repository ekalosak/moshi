#!/bin/bash
PYTHON_VERSION=3.10
echo "👋 Installing Moshi..."
echo "👉 whoami: $(whoami)"
echo "👉 shell: $SHELL"
export PYENV_ROOT="$HOME/.pyenv" && \
export PATH="$PYENV_ROOT/bin:$PATH" && \
echo $PYENV_ROOT && echo $PATH && \
eval "$(pyenv init -)" && \
pyenv versions && \
pyenv update && \
echo "🔧 Creating virtual environment..." && \
pyenv virtualenv $PYTHON_VERSION moshi && \
echo "✅ Python virtual environment created!" && \
pyenv activate moshi && \
echo "✅ Python virtual environment activated!" && \
echo "🔧 Installing keyring..." && \
yes | pip install --upgrade pip && \
yes | pip install \
  keyring \
  keyrings.google-artifactregistry-auth && \
mkdir -p ~/.config/pip && \
mv pip.conf ~/.config/pip/pip.conf && \
echo "✅ Keyring installed!" && \
echo "👉 Keyrings:" && \
keyring --list-backends && \
echo "🔧 Installing moshi..." && \
yes | pip install \
  --extra-index-url https://us-central1-python.pkg.dev/moshi-3/moshi/simple \
  gunicorn moshi && \
pyenv deactivate && \
echo "from moshi.api.core import app" > main.py && \
echo "✅ Moshi installed!"