#!/bin/bash
# For setting up VMs (Deterministic Instance Template)
PYTHON_VERSION=3.10
sudo apt-get -y update && \
  sudo apt-get -y install git build-essential \
    zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev liblzma-dev && \
  curl https://pyenv.run | bash && \
  export PYENV_ROOT="$HOME/.pyenv" && \
  export PATH="$PYENV_ROOT/bin:$PATH" && \
  eval "$(pyenv init -)" && \
  pyenv update && \
  pyenv install $PYTHON_VERSION && \
  pyenv virtualenv $PYTHON_VERSION moshi && \
  pyenv rehash && \
  pyenv activate moshi && \
  pip install --upgrade pip && \
  pyenv deactivate && \
  sudo apt-get remove -y git build-essential \
    zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev liblzma-dev && \
  sudo apt-get autoremove -y && \
  sudo apt-get clean -y && \
  sudo rm -rf /var/lib/apt/lists/* && \
  echo "✅ Python3 installed!"