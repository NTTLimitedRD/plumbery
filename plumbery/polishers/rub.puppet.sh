#!/usr/bin/env bash

# install puppet
apt-get -y update && apt-get -y install puppet

# apply a manifest eventually
MANIFEST=$1

if [ -f "$MANIFEST" ]
then
    puppet apply --modulepath $MANIFEST
fi
