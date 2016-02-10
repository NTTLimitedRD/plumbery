=====================================
Docker Swarm with multiple containers
=====================================

This is a cluster of coordinated servers with Docker engine.

Requirements for this use case
------------------------------

* Add a Network Domain
* Add an Ethernet network
* Deploy a Ubuntu server as a manager
* Deploy multiple large Ubuntu servers as Docker containers
* Monitor all servers
* Assign a public IPv4 address to all servers
* Add address translation rules to ensure Internet connectivity with each node
* Add firewall rules to accept TCP traffic on port 22 (ssh)
* Install Docker Engine at all nodes
* Install Consul on the manager node to implement dynamic discovery back-end
* Run Docker Swarm Manager on manager node
* Run Docker Swarm at every other node

Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. literalinclude:: ../demos/docker.swarm.yaml
   :language: yaml
   :linenos:


Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

These commands will build fittings as per the provided plan, start all servers
and bootstrap them.

You can find the public address assigned to the manager server like this:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml ping


Follow-up commands
------------------

In this use case you can use the IPv4 assigned to the manager for direct ssh
connection.

.. sourcecode:: bash

    $ ssh ubuntu@<ipv4_here>

From there you will check both the status of the local Docker Engine, and the
status from the full Docker Swarm:

.. sourcecode:: bash

    $ docker info
    $ docker -H :4000 info

Next step is to run a new Redis container somewhere in the swarm:

.. sourcecode:: bash

    $ docker -H :4000 run --name some-redis -d redis

And, of course, you may want to identify which node is running redis
exactly:

.. sourcecode:: bash

    $ docker -H :4000 ps -l | grep redis

Destruction commands
--------------------

The more servers you have, the more costly it is. Would you like to stop the
invoice?

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml dispose

