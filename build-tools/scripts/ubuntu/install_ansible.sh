#!/bin/bash -eu

source /tmp/scripts/generic_functions.sh


install_packages software-properties-common
sudo apt-add-repository -y ppa:ansible/ansible
echo "Upgrading the image..."
apt-get upgrade -y
echo "Installing ansible ..."
install_packages ansible
