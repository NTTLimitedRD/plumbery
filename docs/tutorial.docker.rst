================
Docker container
================

This is a rather big virtual machine with Docker on it.

Requirements for this use case
------------------------------

* Add a Network Domain
* Add an Ethernet network
* Deploy a large Ubuntu server
* Monitor this server
* Assign a public IPv4 address
* Add address translation to ensure end-to-end IP connectivity
* Add firewall rule to accept TCP traffic on port 22 (ssh)
* Install Docker

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

You can find the public address assigned to the web server like this:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml ping


Follow-up commands
------------------

In this use case you can use the IPv4 assigned to the node for direct ssh
connection.

.. sourcecode:: bash

    $ ssh root@<ipv4_here>


You will have to accept the new host, then provide the password used for the
creation of the node.

.. sourcecode:: bash

    $ docker run hello-world


This command is self-explanatory and validates the setup of Docker.

Destruction commands
--------------------

The more servers you have, the more costly it is. Would you like to stop the
invoice?

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy

