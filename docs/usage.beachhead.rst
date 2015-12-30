============================
How to beachhead on the MCP?
============================

In many cloud deployments, the appropriate strategy is to run administration
servers directly in the cloud. This usually facilitates a lot end-to-end
connectivity to the other nodes. For example, Dimension Data provides
IPv6 connectivity between all data centres. However, very few companies today
can benefit from IPv6 from corporate workstations.

Requirements for this use case
------------------------------

* Deploy a Network Domain
* Deploy a network dedicated to management servers
* Deploy a Ubuntu server named ``beachhead``
* Monitor this node
* Assign a public IPv4 address to ``beachhead`` and add NAT
* Add firewall rule to accept TCP traffic on port 22 (ssh)


Fittings plan
-------------

In the example below we selected to beachhead at Frankfurt. Of course, you can
use a different locationID, or even a different region.
Content of ``fittings.yaml``:

.. sourcecode:: yaml

    ---
    safeMode: False
    ---
    # Frankfurt in Europe
    locationId: EU6
    regionId: dd-eu

    blueprints:

      - beachhead:
          domain:
            name: Acme
            service: advanced
            ipv4: 2
          ethernet:
            name: acme.control
            subnet: 10.0.0.0
            destroy: never
          nodes:
            - beachhead:
                description: '#beachhead #ops'
                glue:
                  - internet 22
                running: always
                monitoring: essentials

In this example, the plan is to deploy a single node in the data centre
at Frankfurt, in Europe. The node ``beachhead`` is placed in a
network named ``acme.control``, and the network is part of a network
domain acting as a virtual data centre, ``Acme``. The blueprint has a
name, ``beachhead``, so that it can be handled independently from
other blueprints.

Some notes on directives used in these fittings plan:

* ``service: advanced`` - Dimension Data provides several flavours of Network
  Domains. Here the decision is to deploy an ``advanced`` domain

* ``ipv4: 2`` - This is to reserve some public IPv4 addresses. Here we anticipate
  on the public address assigned to the ``beachhead`` node.

* ``destroy: never`` - This directive prevents plumbery from destroying a network.
  In other terms, the command ``python -m plumbery destroy beachhead`` will not
  actually destroy the network ``acme.control``. You may have to go to CloudControl
  and to destroy the network manually if needed.

* ``glue:`` - This directive adds connectivity to a node, either by assigning
  a public IPv4 address to the Internet, or by adding network interfaces to
  additional networks. With ``internet 22``, Plumbery assigns a public IPv4
  address and adds a NAT rule to the firewall.

* ``running: always`` - This directive prevents plumbery from stopping the node.
  In other terms, the command ``python -m plumbery stop beachhead`` is inoperative.
  And because plumbery cannot destroy a running node, this directive also
  prevents the deletion of ``beachhead``.

* ``monitoring: essential`` - Automatically adds monitoring to this node after
  its creation.

Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml build beachhead
    $ python -m plumbery fittings.yaml start beachhead

These two commands will build fittings as per the provided plan, and start
the target node also.

Follow-up commands
------------------

In this use case you can use the IPv4 assigned to the node for direct ssh
connection.

.. sourcecode:: bash

    $ ssh root@<ipv4_here>


You will have to accept the new host, then provide the password used for the
creation of the node ``beahhead``.

After that you can do whatever you want on this first host. For example, you may
want to update the software, to install libcloud and plumbery:

.. sourcecode:: bash

    $ apt-get update
    $ apt-get upgrade
    $ apt-get install python-pip python-dev git
    $ pip install -e git+https://git-wip-us.apache.org/repos/asf/libcloud.git@trunk#egg=apache-libcloud
    $ pip install -e git+https://github.com/bernard357/plumbery.git#egg=plumbery
    $ python -m plumbery -v

Then follow instructions from :doc:`getting_started` to finalize the setup
of the environment at ``beachhead`` : credentials to Dimension Data cloud
services, etc.

