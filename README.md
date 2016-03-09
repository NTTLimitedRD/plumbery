[![Build status](https://img.shields.io/travis/DimensionDataCBUSydney/plumbery.svg)](https://travis-ci.org/DimensionDataCBUSydney/plumbery)  ![Python 2.7](https://img.shields.io/badge/python-2.7-blue.svg)

# plumbery

Are you looking for a cloud plumber? We hope that this one will be useful to
you.


## Infrastructure as code at Dimension Data with Apache Libcloud

* Documentation: [Plumbery at ReadTheDocs](https://plumbery.readthedocs.org)
* Python package: [Plumbery at PiPy](https://pypi.python.org/pypi/plumbery)
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



