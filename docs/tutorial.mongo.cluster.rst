======================
How to deploy MongoDB?
======================

MongoDB is a database that is really well-adapted to real-time data analytics.
In this tutorial we will deploy multiple servers, and glue them together.

Requirements for this use case
------------------------------

* Add a Network Domain
* Add an Ethernet network
* Deploy multiple servers servers
* Monitor these servers
* Add mongoDB to the servers
* Create a cluster of configuration servers
* Add sharding servers


Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. literalinclude:: ../demos/mongo.yaml
   :language: yaml
   :linenos:

Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml build
    $ python -m plumbery fittings.yaml start
    $ python -m plumbery fittings.yaml rub

These commands build fittings as per the provided plan, start the server
and bootstrap it. The last command will display the name and password
used to configure the database.

You can check status of servers like this:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml ping

Follow-up commands
------------------

TO BE COMPLETED

Destruction commands
--------------------

The more servers you have, the more costly it is. Would you like to stop the
invoice?

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy

