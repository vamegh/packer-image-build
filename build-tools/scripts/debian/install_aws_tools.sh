#!/bin/bash -eu

source /tmp/scripts/generic_functions.sh

# curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

install_deb_packages python3 python3-pip python-pip curl apt-transport-https ca-certificates software-properties-common gnupg-agent

## Install the latest versions of the various boto / awscli utilities
sudo -H pip install awscli boto botocore boto3
sudo -H pip3 install awscli boto botocore boto3



