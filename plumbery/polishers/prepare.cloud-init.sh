#!/usr/bin/env bash

# consider popular installers

apt=`command -v apt-get`
yum=`command -v yum`
zypper=`command -v zypper`

if [ -n "$apt" ]; then
    apt-get -y update
    apt-get -q -y install cloud-init

elif [ -n "$yum" ]; then
    yum -y install cloud-init

elif [ -n "$zypper" ]; then
    zypper --non-interactive addrepo http://download.opensuse.org/repositories/Cloud:/Tools/SLE_11_SP3/Cloud:Tools.repo
    zypper --gpg-auto-import-keys refresh
    zypper --non-interactive install cloud-init

else
    echo "Error: no path to apt-get or yum or zypper" >&2;
    exit 1;
fi

# allow for repeated prepare
rm -rf /var/lib/cloud/instance*


