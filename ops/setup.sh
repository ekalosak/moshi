#!/bin/bash
# For setting up VMs (Deterministic Instance Template)
PYTHON_VERSION=3.10
sudo apt-get -y update && \
  sudo apt-get -y install git && \
  sudo apt-get -y build-dep python3 && \
  curl https://pyenv.run | bash && \
  echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc && \
  echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc && \
  echo 'eval "$(pyenv init -)"' >> ~/.bashrc
