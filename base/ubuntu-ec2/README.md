# BASE AMI BUILD

# Jenkins Master AMI BUILD

## Modifications,

All of the various configuration parameters are set inside variables.json, please modify this file - unless of course there is a necessary change to the packer settings.

## Running Packer:

```packer build -var-file=variables.json packer.json```
