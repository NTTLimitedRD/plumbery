#!/usr/bin/env bash

# consider popular installers

apt=`command -v apt-get`
yum=`command -v yum`

if [ -n "$apt" ]; then
    apt-get -y update
    apt-get -q -y install cloud-init

elif [ -n "$yum" ]; then
    yum -y install cloud-init

else
    echo "Error: no path to apt-get or yum" >&2;
    exit 1;
fi

# allow for repeated prepare
rm -rf /var/lib/cloud/instance*


