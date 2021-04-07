# AMI / Packer Builds - The immutable way

This is pretty rough and requires quite a bit of clean up still. 

## Build instructions

First configure your user here: [ansible/users.yml](ansible/users.yml)

Add your ssh public key to: [build-tools/files/public_keys/](build-tools/files/public_keys/)

Then run the following:

```
cd base/ubuntu-ec2/
./run-packer.sh
cd ../../
cd web/ubuntu-ec2/
./run-packer.sh
cd ../../
```

After the above is run the ubuntu base image should be built along with the web based image, they both should be available as ami images in Amazon ec2.


