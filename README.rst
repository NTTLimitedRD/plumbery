===============================
Plumbery
===============================

.. image:: https://img.shields.io/pypi/v/plumbery.svg
        :target: https://pypi.python.org/pypi/plumbery

.. image:: https://img.shields.io/travis/DimensionDataCBUSydney/plumbery.svg
        :target: https://travis-ci.org/DimensionDataCBUSydney/plumbery

.. image:: https://coveralls.io/repos/github/DimensionDataCBUSydney/plumbery/badge.svg?branch=master
   :target: https://coveralls.io/github/DimensionDataCBUSydney/plumbery?branch=master

.. image:: https://readthedocs.org/projects/plumbery/badge/?version=latest
   :target: http://plumbery.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/pypi/l/plumbery.svg?maxAge=2592000
   :target: https://pypi.python.org/pypi/plumbery

.. image:: https://img.shields.io/pypi/pyversions/plumbery.svg?maxAge=2592000
   :target: https://pypi.python.org/pypi/plumbery


Infrastructure as code at Dimension Data with Apache Libcloud

* Documentation: `Plumbery at ReadTheDocs`_
* Python package: `Plumbery at PyPi`_
* Source code: `Plumbery at GitHub`_
* Free software: `Apache License (2.0)`_

Features
--------

* 41 tutorials covering popular use cases
* Read fittings plan in YAML
* Load parameters in separate YAMl file
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
* Set private IPv4 statically
* Add public IPv4 addresses to nodes
* Add monitoring to nodes
* Add backup to nodes
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
* You can extend plumbery with your own software, it has been designed for that
* Run from the command line, or as a python library
* Accept custom actions from the command line too
* Limit plumbing to some locations if needed

Contributors
------------

* `Bernard Paques`_ [Dimension Data employee] (development lead)
* `Anthony Shaw`_ [Dimension Data employee]
* `Olivier Grosjeanne`_ [Dimension Data employee]
* `Jacques Clément`_ [Dimension Data employee]
* `Asim Khawaja`_ [Dimension Data employee]

Credits
-------

* `Cloud-Init`_
* `Apache Libcloud`_
* netifaces_
* PyYAML_
* Cookiecutter_
* `cookiecutter-pypackage`_

.. _`Plumbery at ReadTheDocs`: https://plumbery.readthedocs.org
.. _`Plumbery at PyPi`: https://pypi.python.org/pypi/plumbery
.. _`Plumbery at GitHub`: https://github.com/DimensionDataCBUSydney/plumbery
.. _`Apache License (2.0)`: http://www.apache.org/licenses/LICENSE-2.0
.. _`Bernard Paques`: https://github.com/bernard357
.. _`Anthony Shaw`: https://github.com/tonybaloney
.. _`Olivier Grosjeanne`: https://github.com/job-so
.. _`Jacques Clément`: https://github.com/jacquesclement
.. _`Asim Khawaja`: https://github.com/asimkhawaja
.. _`Cloud-Init`: https://cloudinit.readthedocs.org/en/latest/topics/examples.html
.. _`Apache Libcloud`: https://libcloud.apache.org/
.. _netifaces: https://pypi.python.org/pypi/netifaces
.. _PyYAML: https://pypi.python.org/pypi/PyYAML
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
