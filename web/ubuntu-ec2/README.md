# DOOST2 WEB AMI BUILD

## Modifications,

All of the various configuration parameters are set inside variables.json, please modify this file - unless of course there is a necessary change to the packer settings.

Currently mysql is packaged with this build, mysql is also available in its own stand-alone instance.


## Running Packer:

```packer build -var-file=variables.json packer.json```
