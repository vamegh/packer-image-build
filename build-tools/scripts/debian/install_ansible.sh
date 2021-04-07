#!/bin/bash -eu

source /tmp/scripts/generic_functions.sh


install_deb_packages software-properties-common
#sudo echo 'deb "http://ppa.launchpad.net/ansible/ansible/ubuntu trusty main"' > /etc/apt/sources.list.d/ansible.list
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 93C4A3FD7BB9C367
sudo add-apt-repository \
   "deb http://ppa.launchpad.net/ansible/ansible/ubuntu \
   trusty \
   main"

sudo ex +"%s@DPkg@//DPkg" -cwq /etc/apt/apt.conf.d/70debconf
sudo dpkg-reconfigure debconf -f noninteractive -p critical
install_deb_packages ansible
sudo apt-get upgrade -y


