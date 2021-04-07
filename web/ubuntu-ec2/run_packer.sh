#!/bin/bash

echo "Configuring variables.json"
#rm -f ${account_name}_variables.json
python3 ../../build-tools/python/configure_packer.py

account_name=`cat account|tr -d '\n'`

echo "Running packer"
packer build -var-file=${account_name}_variables.json packer.json

rm -f account
