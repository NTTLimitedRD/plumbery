===========
Docker node
===========

Despite the surging interest in containers, the community is still struggling
on the proper setup of a Docker node. In other terms, the handling of containers
is really a breeze compared to previous situation. However, there is a need
to facilitate the deployment of the underlying infrastructure, including the
network and the security.

.. image:: tutorial.docker.png

In this tutorial we demonstrate how to create a class of Docker nodes and deploy
one single node. Of course, you can use this file for yourself, and change it
to better accomodate your requirements. For example, duplicate the last section
of this fittings plan and mention other data centres and regions.

Requirements for this use case
------------------------------

* Add a Network Domain
* Add an Ethernet network
* Deploy a large Ubuntu server
* Provide 32 CPU and 256 MB of RAM to each node
* Add a virtual disk of 100 GB
* Monitor this server in the real-time dashboard
* Assign a public IPv4 address to each node
* Add address translation to ensure end-to-end IP connectivity
* Add firewall rule to accept TCP traffic on port 22 (ssh)
* Combine the virtual disks into a single expanded logical volume (LVM)
* Install a new SSH key to secure remote communications
* Configure SSH to reject passwords and to prevent access from root account
* Install Docker
* Allow non-root account to use Docker

Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. literalinclude:: ../demos/docker.yaml
   :language: yaml
   :linenos:


Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

These commands will build fittings as per the provided plan, start the server
and bootstrap it.

You can find the public address assigned to the Docker node like this:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml information


Follow-up commands
------------------

In this use case you can use the IPv4 assigned to the node for direct ssh
connection.

.. sourcecode:: bash

    $ ssh ubuntu@<ipv4_here>


You will have to accept the new host, and authentication will be based on
the SSH key communicated to the node by Plumbery.

.. sourcecode:: bash

    $ docker run hello-world


This command is self-explanatory and validates the setup of Docker.

Destruction commands
--------------------

Launch following command to remove all resources involved in the fittings plan:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml dispose

