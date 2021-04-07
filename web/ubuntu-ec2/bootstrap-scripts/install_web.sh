#!/bin/bash -eu

source /tmp/scripts/generic_functions.sh

export LANG=C.UTF-8

# Set Local Variables
bin_path=/usr/local/bin

install_packages bzip2 unzip xz-utils git lcov vim-nox wget curl sudo jq apache2-utils apache2

sudo systemctl daemon-reload


