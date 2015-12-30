.. :changelog:

History
-------

0.3.3 (2015-12-31)
~~~~~~~~~~~~~~~~~~

* Create load balancers with pools of nodes
* Streamline messages in safe mode
* Options to run in debug or in quiet mode
* Load fittings plan as a string
* Limit plumbing to some locations if needed
* Make flake8 as happy as possible (PEP8 enforcement)
* Add software documentation for polishers ansible, inventory and rub
* Split software documentation in multiple pages
* Add a first documented use case to the on-line documentation
* Restructure code of the core engine
* Passing Travis CI
* Test coverage 39%

0.3.2 (2015-12-23)
~~~~~~~~~~~~~~~~~~

* Run plumbery from the command-line
* Accept custom polisher from the command line too
* Release the first comprehensive on-line documentation at ReadTheDocs
* Illustrate new features in one demonstration fittings plan (the Gigafox project)
* Consolidate sample scripts and python programs for demonstrations
* Allow multiple network interfaces per node
* Reserve and manage pools of public IPv4 addresses
* Add address translation to nodes equipped with public IPv4 addresses
* Add firewall rules for nodes directly visible from the internet
* Wait for nodes to be deployed before polishing them
* Add new strategies to communicate with nodes over the network
* Fix the usage of puppet for Apache nodes
* Improve reporting messages
* Enhance code documentation
* Fix behaviour on multiple abnormal conditions
* Passing Travis CI
* Test coverage 40%

0.2.4 (2015-12-13)
~~~~~~~~~~~~~~~~~~

* Extend coverage of the Gigafox project
* Add monitoring to nodes created
* Run polisher 'spit' right after build to finalise setup of nodes
* Produce inventory with polisher of same name
* Introduce puppet manifests to polisher 'rub'
* Add file copy to remote nodes
* Introduce basement blueprints
* Improve reporting messages
* Enhance code documentation
* Fix behaviour on abnormal situations
* Passing Travis CI
* Test coverage 46%

0.2.3 (2015-12-07)
~~~~~~~~~~~~~~~~~~

* Introduce Gigafox project, to demonstrate deployment across multiple places
* Create firewall rules to allow traffic between networks
* Cache information to save on API calls and to accelerate the processing
* Improve the state engine
* Passing Travis CI
* Test coverage 48%

0.2.2 (2015-12-05)
~~~~~~~~~~~~~~~~~~

* Use ipv6 when possible to connect to remote nodes
* Manual tests to improve usage on specific conditions, e.g., against MCP 1.0
* Label expansion to facilitate node handling, e.g., mongo[1..20]
* Allow for destruction of networks and of domain networks
* Passing Travis CI
* Test coverage 55%

0.2.1 (2015-12-02)
~~~~~~~~~~~~~~~~~~~

* Code refactoring into a new module for nodes
* fake8 complains only about long lines and line termination
* Passing Travis CI
* Test coverage 59%

0.2.0 (2015-11-29)
~~~~~~~~~~~~~~~~~~

* Allow for node bootstrapping via SSH
* Push SSH public key
* Update Linux packages
* Install Docker
* Provide an inventory of running nodes
* Build inventory for ansible
* Extension mechanism called polishers
* Add demonstration scripts related to polishers
* A lot of docstring has been added
* fake8 complains only about long lines and line termination
* Passing Travis CI
* Test coverage 59%

0.1.2 (2015-11-27)
~~~~~~~~~~~~~~~~~~

* First pull request fully processed
* Docstring for all modules
* Passing Travis CI
* Test coverage 62%

0.1.0 (2015-11-20)
~~~~~~~~~~~~~~~~~~

* First release on PyPI.
