.. :changelog:

History
-------

0.8.1 (2016-05-23)
~~~~~~~~~~~~~~~~~~

* Remove windows line endings from unix shell fixtures.

0.8.0 (2016-04-13)
~~~~~~~~~~~~~~~~~~

* Add the capability to backup nodes

0.7.0 (2016-04-06)
~~~~~~~~~~~~~~~~~~

* Rename 'spit' to 'configure'

0.6.0 (2016-03-15)
~~~~~~~~~~~~~~~~~~

* Added private MCP support (compute only)
* Updated Dockerfile to support parameters
* Set 'finalize' (or 'finalise' for the English) as the new phrase for 'polish'
* Removed coordinate and city lookups (we are adding 40 MCPs this year, I really don't want to maintain that list!)

0.5.0 (2016-03-13)
~~~~~~~~~~~~~~~~~~

* Handover project governance to Dimension Data R&D team
* 26 tutorials are now provided in separate plumbery-contribs project at GitHub
* Introduce deployment parameters (location, domain name, network name, ...)
* Add tutorial on log consolidation (ELK)
* Add tutorial on disk orchestration (standard, high-performance, economy)
* Secure SSH communications in most tutorials (no password, no root access)
* Add virtual storage to many tutorials
* Derive regionId from locationId to streamline fittings plan
* Add action 'refresh' to ease iterations in fittings plan
* Add option -p to load parameters from the command line
* Accept web links for fittings plan and for parameters file
* Restructure code to accomodate for more complex data processing
* Fix multiple bugs and errors
* Augment test coverage
* Improve information provided in debug mode
* Passing Travis CI
* 3286 python statements
* Test coverage 53%

0.4.3 (2016-02-28)
~~~~~~~~~~~~~~~~~~

* A total of 24 various tutorials is provided
* Enhance tutorials on Docker and Kubernetes with virtual storage, SSH keys, class-based definition, and updated tutorial
* Add tutorial on iTop, an open source solution for ITIL management
* Add the management of virtual disks, including tiered storage
* Add tutorial showing partitioning, formatting and mounting of virtual disks
* Enhance the usage documentation page
* Accept pseudo-target of blueprints
* Add classes of nodes to streamline large deployments
* Include the library of Customer Images
* Normalize information reported by the 'inventory' command
* Expose geolocalisation information to nodes if needed
* Generalize the usage of 'information:' to support active documentation of fittings plans
* Put fittings plan in context with the new 'links:' directive
* Reduce requirements in fittings plan passed as a Python dictionary
* Add power off as secondary mechanism to stop nodes, when graceful shutdown is not enough
* Allow for CPU and memory dynamic reconfiguration
* Add option -s to run plumbery in safe mode from the command line
* Report on time spent in the cloud while working
* Fix multiple bugs and errors
* Augment test coverage
* Improve information provided in debug mode
* Passing Travis CI
* 3121 python statements
* Test coverage 50%

0.4.2 (2016-02-14)
~~~~~~~~~~~~~~~~~~

* Add tutorials on Docker, Kubernetes, Docker Swarm -- DevOps
* Add tutorial to create a Stackstorm server -- DevOps too
* Add tutorial to create a swarm of pingers with MQTT and Kibana -- IOT is coming
* A total of 23 various tutorials is provided
* Enhance the documentation accordingly
* Enhance the documentation page on cloud-config
* Add help for Windows users
* Add the generation of uuid when needed (ceph cluster)
* Add the capability to assign public IPv4 when needed (automatic mode)
* Expand information reported by the 'inventory' command
* Now support settings for a proxy for all interactions with API endpoints
* Restructure code and improve performance with better cache
* Fix multiple bugs and errors
* Improve information provided in debug mode
* Passing Travis CI
* 2769 python statements
* Test coverage 48%

0.4.1 (2016-01-24)
~~~~~~~~~~~~~~~~~~

* Provision of an advanced tutorial that demonstrates most interesting features
* A total of 18 various tutorials is provided
* Enhance the documentation accordingly
* Leverage cloud-init with global directives shared by all nodes
* Extend dynamic variables to random, on-demand RSA keys
* Enforce password-free communications, and ipv6 communications
* Add actions 'wipe' and 'secrets'
* Restructure code and consolidate functions
* Fix multiple bugs and errors
* Expand information provided in debug mode
* Passing Travis CI
* 2717 python statements
* Test coverage 47%

0.4.0 (2016-01-17)
~~~~~~~~~~~~~~~~~~

* Add cloud-init for node contextualisation
* Inject dynamic variables (e.g., node addresses) to node contextualisation
* Generate and store random secrets for secured node contextualisation
* Enhance usage page in the documentation
* Add a full pack of tutorials in the on-line documentation
* Add actions 'deploy' and 'dispose' to streamline usage
* Add polishers 'ping' and 'information'
* Restructure code and consolidate functions
* Fix multiple bugs and errors
* Expand information provided in debug mode
* Passing Travis CI
* Test coverage 47%

0.3.4 (2016-01-06)
~~~~~~~~~~~~~~~~~~

* Add tutorials to the documentation
* Fix some errors
* Expand information provided in debug mode
* Passing Travis CI
* Test coverage 39%

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
