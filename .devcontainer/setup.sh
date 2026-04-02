#!/bin/bash
# Ensure system packages are updated
# DanB - added the noninteractive and force because I was getting dialog about configuring
# openssh-server and the version of the sshd_config file.  This says keep the existing file.
# I kept the existing file only because I don't know why I want to replace it.
sudo DEBIAN_FRONTEND=noninteractive UCF_FORCE_CONFFOLD=1 apt update && sudo DEBIAN_FRONTEND=noninteractive UCF_FORCE_CONFFOLD=1 apt upgrade -y

# Install extra system dependencies if needed
sudo apt install -y build-essential curl git unzip zip git-lfs

# Install additional Python packages
pip install --upgrade pip

# Except for the ipyXXX packages that we don't need, the rest should get
# installed when we install this repo.
# pip install numpy pandas matplotlib seaborn ipykernel ipywidgets

# DanB - Don't think we need this for malaria.
# Ensure git lfs is installed and pull LFS files
#git lfs install
#git lfs pull

# dev install emodpy-malaria (can be replaced later by pip install emodpy-malaria from jfrog)
pip install -e . --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
# install idmtools
pip install idmtools[full] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple --upgrade --force-reinstall
pip install idmtools-test --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple  --upgrade --force-reinstall
