#!/bin/bash
PYTHON_VERSION=3.10
echo "👉 whoami: $(whoami)"
echo "👉 PYTHON_VERSION: $PYTHON_VERSION"
cd ~ && \
    echo "🔧 Installing pyenv..." && \
    curl https://pyenv.run | bash && \
    export PYENV_ROOT="$HOME/.pyenv" && \
    export PATH="$PYENV_ROOT/bin:$PATH" && \
    eval "$(pyenv init -)" && \
    pyenv update && \
    echo "✅ pyenv installed to: $(which pyenv)!" && \
    echo "🔧 Installing Python3..." && \
    pyenv install $PYTHON_VERSION && \
    pyenv rehash && \
    echo "✅ Python3 installed!" && \
    echo "🔧 Creating virtual environment..." && \
    pyenv virtualenv $PYTHON_VERSION moshi && \
    echo "✅ Python virtual environment created!"