===============================
plumbery
===============================

.. image:: https://img.shields.io/pypi/v/plumbery.svg
        :target: https://pypi.python.org/pypi/plumbery

.. image:: https://img.shields.io/travis/bernard357/plumbery.svg
        :target: https://travis-ci.org/bernard357/plumbery

.. image:: https://readthedocs.org/projects/plumbery/badge/?version=latest
        :target: https://readthedocs.org/projects/plumbery/?badge=latest
        :alt: Documentation Status


Cloud automation at Dimension Data with Apache Libcloud

* Free software: Apache License (2.0)
* Documentation: https://plumbery.readthedocs.org.

Features
--------

* Read fittings plan in YAML
* Use cloud API to create the network infrastructure, and to build nodes
* Build all blueprints
* Build one single blueprint across multiple locations
* Start all nodes
* Start nodes belonging to the same blueprint
* Polish all Linux nodes for quick bootstrapping
* Build a full inventory of nodes that have been deployed
* Reflect fittings into a ready-to-use inventory for ansible
* Stop all nodes
* Stop nodes belonging to the same blueprint
* Destroy all nodes
* Destroy nodes belonging to the same blueprint
* Many demonstration scripts are provided
* You can extend plumbery with your own polishers, it has been designed for that

Credits
---------

*  `Apache Libcloud`_
*  netifaces_
*  PyYAML_
*  Cookiecutter_
*  `cookiecutter-pypackage`_

.. _`Apache Libcloud`: https://libcloud.apache.org/
.. _netifaces: https://pypi.python.org/pypi/netifaces
.. _PyYAML: https://pypi.python.org/pypi/PyYAML
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
