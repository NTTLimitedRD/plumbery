==============================
Cluster of Apache2 web servers
==============================

In this tutorial we will deploy multiple web servers, and arrange
them in a single pool driven by a load-balancer.

Requirements for this use case
------------------------------

* Deploy a cluster of 10 web servers in London
* Add a Network Domain
* Add an Ethernet network
* Deploy 10 utility web servers
* Monitor these servers
* Pool these servers
* Add a listener and configure load-balancing


Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. code-block:: yaml
   :linenos:

    # London
    locationId: EU8
    regionId: dd-eu

    blueprints:

      - web:

          domain:
            name: Acme
            ipv4: 2
            service: advanced

          ethernet:
            name: acme.control
            subnet: 10.0.0.0

          nodes:

            - web[1..10]:
                description: '#apache #eu'
                monitoring: essentials

          listeners:

            - http:
                port: 80
                protocol: http
                algorithm: round_robin

Some notes on directives used in these fittings plan:

``ipv4: 2`` - Some public address is required for the listening address
of the load-balancer

``web[1..10]_eu8`` - This notation allows to handle multiple nodes in a
compact directive. Here plumbery will create ``web1_eu8``, ``web2_eu8``, etc.
Indicate the minimum and the maximum numbers, and plumbery will populate
the full range. This is so powerful for collections of similar nodes!

``prepare:`` - These are directives reserved to the polisher ``prepare``, and applied
to each node via ssh connection. The first step is to copy a Puppet manifest
to each node with ``put prepare.puppet.apache.pp /root/apache.pp``. Then a script
is applied to install Puppet, and to apply the provided manifest.

``listeners:`` - On this directive, Plumbery will put all nodes of this
blueprint in the same pool, and configure the load-balancer. Settings provided
in this sample plan are adapted to a bare web server.


Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

This command will build fittings as per the provided plan, and start
the target node also.

Follow-up commands
------------------

Ideally each web server would be connected to a Puppet server for automatic
configuration of the cluster. Here we have provided a simplistic example
of a masterless configuration, to give you an idea.

Destruction commands
--------------------

The more servers you have, the more costly it is. Would you like to stop the
invoice?

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy

