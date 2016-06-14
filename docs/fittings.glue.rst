Connecting nodes to the Internet and to networks
================================================

By default, plumbery connects each node to the network that is defined in the same
blueprint. In the following example, the node ``myServer`` has a primary
network interface that is plugged into the VLAN ``myNetwork``. Also, the private IPv4
that is assigned to ``myServer`` is taken automatically from the subnet associated with ``myNetwork``.

.. sourcecode:: yaml

    blueprints:

      - myBluePrint:
          domain:
            name: myDC
          ethernet:
            name: myNetwork
            subnet: 10.1.10.0
          nodes:
            - myServer

The directive ``glue:`` will be useful to you if you have to depart from this simple
situation. More specifically:

* to set a fixed private IPv4 address to a node
* to add a public IPv4 address and a NAT rule
* to connect the node to multiple networks

The directive is a list of settings, each one being related to a connection, like in the following example:

.. sourcecode:: yaml

    blueprints:

      - myBluePrint:

          domain:
            name: myDC

            # number of IPv4 addresses to be reserved
            #
            ipv4: 2

          ethernet:
            name: myNetwork
            subnet: 10.1.0.0

          nodes:

            - node1:

                glue:

                  # assign 10.1.0.11 to the primary NIC
                  - primary .11

                  # get a public IPv4 from pool and NAT it to primary NIC and open firewall
                  - internet 22

                  # add secondary NIC
                  - SecondaryNetwork .11

                  # add third NIC
                  - TertiaryNetwork 10.3.0.11


How to set a fixed private IPv4 address?
----------------------------------------

The basic syntax is to mention the name of the primary network, followed by the private IPv4 address to be used.
There are some other possibilities to consider, that can help to streamline the overall configuration.

======================================  ===============================================================================
All these are equivalent                Description
======================================  ===============================================================================
``- myNetwork 10.1.0.11``               Explicit configuration of the network and address
``- myNetwork .11``                     Combine with the network subnet to compute the real address
``- primary 10.1.0.11``                 The keyword ``primary`` is translated to the name of the primary network
``- primary .11``                       Implicit configuration of the network and of the address
======================================  ===============================================================================

All configurations mentioned in the table are equivalent. However, ``primary .11`` is probably the easier format to maintain
over time, since it can adapt automatically to a change in network name or in subnet range.

How to expose a node to the Internet?
-------------------------------------

When a line starts with the keyword ``internet`` then plumbery knows that it has to assign a public IPv4 address, to add a NAT rule, and to add
firewall rules as well.

================================================  ===============================================================================
Examples                                          Description
================================================  ===============================================================================
``- internet icmp``                               Add a public IPv4 address, a NAT rule, and allow for ping traffic, but not more
``- internet 22``                                 Allow for ssh traffic from public Internet
``- internet icmp 22 80 443``                     Allow for ping, ssh, http and https traffic from public Internet
``- internet 22 80 1935 9123 udp:16384..32768``   Good for real-time web conferences with BigBlueButton servers
================================================  ===============================================================================

Note: since public IPv4 addresses are needed for this configuration, you have to adjust the directive ``ipv4:`` accordingly.
See :doc:`fittings.domain` for more information.

How to connect a node to multiple networks?
-------------------------------------------

If a node has to be connected to multiple networks,
Simply add one line per target network to deploy a node with multiple connections. If you mention only the name of a network,
an IPv4 address will be automatically assigned from the related subnet. Else you can explicit a private IPv4 address if needed.

================================================  ===============================================================================
Examples                                          Description
================================================  ===============================================================================
``- SecondaryNetwork``                            Add a NIC and an IPv4 address from the related subnet
``- SecondaryNetwork 10.2.0.11``                  Add a NIC and assign this address to it
``- SecondaryNetwork .11``                        Add a NIC and combine with the subnet to compute the resulting address
================================================  ===============================================================================

Important note: when a virtual network interface is added to a node there may be a need to alter the configuration
of the operating system as well. For example, edit ``/etc/network/interface`` under Ubuntu to add ``eth1`` and to configure it.
