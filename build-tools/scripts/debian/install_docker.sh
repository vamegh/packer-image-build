#!/bin/bash -eu

source /tmp/scripts/generic_functions.sh

remove_packages docker docker-engine docker.io containerd runc
install_deb_packages apt-transport-https ca-certificates curl software-properties-common gnupg-agent

curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable"

install_packages docker-ce docker-ce-cli containerd.io docker-compose
