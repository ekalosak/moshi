#!/bin/bash
PYTHON_VERSION=3.10
cd /home/moshi
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
# echo "🔧 Configuring pip..." && \
# mkdir -p ~/.config/pip && \
# mv ~/pip.conf ~/.config/pip/pip.conf && \
# echo "✅ Pip configured!" && \
echo "🔧 Installing moshi..." && \
# yes | pip install --index-url https://us-central1-python.pkg.dev/moshi-3/moshi/simple/ -v moshi && \
pip install --extra-index-url https://us-central1-python.pkg.dev/moshi-3/pypi/simple moshi && \
pyenv deactivate && \
echo "from moshi.api.core import app" > main.py && \
echo "✅ Moshi installed!"