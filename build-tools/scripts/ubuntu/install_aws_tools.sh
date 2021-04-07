#!/bin/bash -eu

source /tmp/scripts/generic_functions.sh

# curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

install_packages curl apt-transport-https ca-certificates software-properties-common gnupg-agent
install_packages python3 python3-pip python3-virtualenv python3-venv python3-wheel python-pip-whl virtualenv virtualenvwrapper

## Install the latest versions of the various boto / awscli utilities
sudo -H pip3 install awscli boto botocore boto3



