[![Build status](https://img.shields.io/travis/DimensionDataCBUSydney/plumbery.svg)](https://travis-ci.org/DimensionDataCBUSydney/plumbery)  ![Python 2.7](https://img.shields.io/badge/python-2.7-blue.svg)

# plumbery

Are you looking for a cloud plumber? We hope that this one will be useful to
you.

## What does plumbery do?

Plumbery is a command-line utility for both Windows and Linux that takes a "fittings file", which is a file describing your desired cloud infrastructure on the Dimension Data Cloud and builds it for you.
Plumbery is idempotent, so you can run it multiple times with the same outcome.

Plumbery also includes a library of example "post-deploy" scripts, supporting cloud-config, for Linux distributions.

A Fittings file is written in a basic YAML file, which can be either HTTP path, or a local file path

```yaml
locationId: EU6
regionId: dd-eu

blueprints:

  - myBluePrint:
      domain:
        name: myDC
      ethernet:
        name: myVLAN
        subnet: 10.1.10.0
      nodes:
        - myServer
```

This will provision:

* A Network Domain called "myDC"
* A VLAN inside that domain called "myVLAN" with the subnet 10.1.10.0/24
* A server called "myServer" with a primary NIC on "myVLAN"

Fittings files can be deployed in a single command

```bash
$ python -m plumbery fittings.yaml deploy
```

## Post-Deploy actions and cloud-config support

Having actions run on the server, immediately after deployment is a common use case. Today, without plumbery this poses a challenge. Plumbery supports cloud-init's cloud-config syntax so post-deploy comamnds like:

* Install packages
* Setup DevOps tools like Puppet, Chef, Salt agent
* Set SSH private keys
* Create users
* Map disk partitions
* Run arbitrary commands

```yaml
  nodes:

    - myServer:
       cloud-config:
         users:
           - name: demo
             groups: sudo
             shell: /bin/bash
             sudo: ['ALL=(ALL) NOPASSWD:ALL']
             ssh-authorized-keys:
               - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDf0q4PyG0doiBQYV7OlOxbRjle026hJPBWD+eKHWuVXIpAiQlSElEBqQn0pOqNJZ3IBCvSLnrdZTUph4czNC4885AArS9NkyM7lK27Oo8RV888jWc8hsx4CD2uNfkuHL+NI5xPB/QT3Um2Zi7GRkIwIgNPN5uqUtXvjgA+i1CS0Ku4ld8vndXvr504jV9BMQoZrXEST3YlriOb8Wf7hYqphVMpF3b+8df96Pxsj0+iZqayS9wFcL8ITPApHi0yVwS8TjxEtI3FDpCbf7Y/DmTGOv49+AWBkFhS2ZwwGTX65L61PDlTSAzL+rPFmHaQBHnsli8U9N6E4XHDEOjbSMRX user@example.com
         runcmd:
           - touch /test.txt
```

## Infrastructure as code at Dimension Data with Apache Libcloud

* Documentation: [Plumbery at ReadTheDocs](https://plumbery.readthedocs.org)
* Python package: [Plumbery at PyPi](https://pypi.python.org/pypi/plumbery)
* Source code: [Plumbery at GitHub](https://github.com/DimensionDataCBUSydney/plumbery)
* Free software: [Apache License (2.0)](http://www.apache.org/licenses/LICENSE-2.0)

## Features

* 24 tutorials covering popular use cases -- DevOps is coming
* Read fittings plan in YAML
* Use cloud API to create the network infrastructure, and to build nodes
* Bootstrap nodes with cloud-init configuration directives
* Inject actual addresses and on-the-fly secrets to contextualisation
* Create RSA keys and passwords to secure deployments
* Preserve random secrets across multiple invocations
* Create network domains and Ethernet networks
* Reserve public IPv4 addresses
* Manage network address translation rules
* Manage firewall rules
* Create load balancers with pools of nodes
* All images in libraries are available to new nodes
* Specify number of CPU, or core per CPU, and CPU speed
* Specify node memory
* Add virtual disks and specify tiers of storage
* Add multiple network interfaces to nodes
* Add public IPv4 addresses to nodes
* Add monitoring to nodes
* Build all blueprints
* Build a blueprint across multiple locations
* Start all nodes
* Start nodes belonging to the same blueprint
* Polish Linux nodes for quick bootstrapping
* Build a full inventory of nodes that have been deployed
* Reflect fittings into a ready-to-use inventory for ansible
* Stop all nodes
* Stop nodes belonging to the same blueprint
* Wipe all nodes
* Wipe nodes belonging to the same blueprint
* Destroy part of the setup, or all blueprints
* Many demonstration scripts are provided
* You can extend plumbery with your own polishers, it has been designed for that
* Run from the command line, or as a python library
* Accept custom polisher from the command line too
* Limit plumbing to some locations if needed



