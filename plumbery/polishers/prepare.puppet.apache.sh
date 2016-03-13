#!/usr/bin/env bash

# install puppet
apt-get -y update && apt-get -y install puppet

# install modules potentially used by manifest
puppet module install puppetlabs-ntp
puppet module install puppetlabs-apache

# apply a manifest eventually
MANIFEST=$1

if [ -f "$MANIFEST" ]
then
    puppet apply $MANIFEST | tee "$MANIFEST.log"
fi
