#!/bin/bash
# For setting up VMs (Deterministic Instance Template)
echo "👋 Setting up Python3 base VM image..."
sudo adduser --system --home /home/moshi --shell /bin/bash moshi && \
  echo "🔧 Installing Python3 build dependencies..." && \
  sudo apt-get -y update && \
  sudo apt-get -y install git build-essential \
    zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev liblzma-dev && \
  sudo -u moshi ./install_pyenv.sh && \
  echo "🔧 Cleaning up..." && \
  sudo apt-get remove -y git build-essential && \
  sudo apt-get autoremove -y && \
  sudo apt-get clean -y && \
  sudo rm -rf /var/lib/apt/lists/* && \
  echo "✅ Base image built!"