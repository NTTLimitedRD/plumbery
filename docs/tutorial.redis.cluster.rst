====================
How to deploy Redis?
====================

Redis is a key-value database that is providing superior performance to
web site and to application servers. In this tutorial we will orchestrate
a cluster of multiple servers.

Requirements for this use case
------------------------------

* Add a Network Domain
* Add an Ethernet network
* Deploy multiple servers servers
* Monitor these servers
* Add redis to the servers
* Configure one server as the master
* Configure other servers to replicate the master


Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. literalinclude:: ../demos/redis.yaml
   :language: yaml
   :linenos:


Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml build
    $ python -m plumbery fittings.yaml start
    $ python -m plumbery fittings.yaml rub

These commands build fittings as per the provided plan, start the server
and bootstrap it. The last command will display the secret used to
authenticate to the redis master server.

You can check status of servers like this:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml ping

Follow-up commands
------------------

After the setup, connect via ssh to redis01 to check the status of the cluster::

    $ ssh root@<ipv4_of_redis01>
    $ redis-cli -h 127.0.0.1 -p 6379
    > AUTH {{ random.secret }}
    OK
    > INFO
    ...
    # Replication
    role:master
    connected_slaves:3

Destruction commands
--------------------

The more servers you have, the more costly it is. Would you like to stop the
invoice?

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy

