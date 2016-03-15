==========================
My first server on the MCP
==========================

Because of sophisticated features brought by the Managed Cloud Platform,
you have to create some infrastructure before landing your first server.
In this tutorial we show how to automate tedious tasks with a couple of
straightforward statements.

Requirements for this use case
------------------------------

* Deploy at Frankfurt in Europe
* Create a Network Domain
* Create an Ethernet network (a VLAN)
* Deploy a first sample server
* Add the server to the automated monitoring dashboard
* Assign a public IPv4 address to the server
* Add address translation to ensure end-to-end IP connectivity
* Add firewall rule to accept TCP traffic on port 22 (ssh)


Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. code-block:: yaml
   :linenos:

    locationId: EU6
    regionId: dd-eu

    blueprints:

      - myBluePrint:
          domain:
            name: myDC
          ethernet:
            name: myVLAN
            subnet: 10.1.10.0
          nodes:
            - myServer

In this example the server ``MyServer`` is placed in a
network named ``MyNetwork``, and the network is part of a network
domain acting as a virtual data centre, ``MyDataCentre``. Feel free to change
these to any values that would better suit you.

Some notes on directives used in these fittings plan:

``locationId: EU6`` and ``regionId: dd-eu`` - The region defines the API
endpoint used by plumbery, and the location designates the target data centre
in the region. Look at the table below to select your preferred location.

  =======================  ============  ==========
  City                      locationId    regionId
  =======================  ============  ==========
  Amsterdam (Netherlands)       EU7        dd-eu
  Ashburn (US East)             NA9        dd-na
  Frankfurt (Germany)           EU6        dd-eu
  Hong Kong                     AP5        dd-ap
  London (UK)                   EU8        dd-eu
  Melbourne (Australia)        AU10        dd-au
  New-Zealand                  AU11        dd-au
  Santa Clara (US West)        NA12        dd-na
  Singapore                     AP3        dd-ap
  Sydney (Australia)            AU9        dd-au
  Tokyo (Japan)                 AP4        dd-ap
  =======================  ============  ==========

``ipv4: 2`` - This is to reserve some public IPv4 addresses. Here we
anticipate on the public address assigned to the server.

``glue:`` - This directive adds connectivity to a node, either by assigning
a public IPv4 address to the Internet, or by adding network interfaces to
additional networks. With ``internet 22``, Plumbery assigns a public IPv4
address and adds a NAT rule. The firewall is also
configured to accept only ssh traffic on port 22.

``monitoring: essential`` - Automatically adds monitoring to this node after
its creation.

Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml build
    $ python -m plumbery fittings.yaml start

These two commands will build fittings as per the provided plan, and start
the server as well. Look at messages displayed by plumbery while it is
working, so you can monitor what's happening.

Follow-up commands
------------------

In this use case you can use the IPv4 assigned to the node for direct ssh
connection.

.. sourcecode:: bash

    $ ssh root@<ipv4_here>


You will have to accept the new host, then provide the password used for the
creation of the server. This is the one put in ``MCP_PASSWORD`` environment
of the computer that is running plumbery.

After that you can do whatever you want on this first host. For example:

.. sourcecode:: bash

    $ apt-get update
    $ apt-get upgrade


Destruction commands
--------------------

Cloud computing has a hard rule. Any resource has a cost, be it used or not.
At the end of every session, you are encouraged to destroy everything.
Hopefully, plumbery is making this really simple:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml dispose

