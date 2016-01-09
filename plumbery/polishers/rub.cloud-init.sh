#!/usr/bin/env bash

# else cloud-init install may fail
apt-get -y update

# install cloud-init itself
apt-get -q -y install cloud-init

# allow for repeated rubs
rm -rf /var/lib/cloud/instance*


