#!/bin/bash

echo "Configuring variables.json"
python3 ../../build-tools/python/configure_packer.py

account_name=`cat account|tr -d '\n'`

