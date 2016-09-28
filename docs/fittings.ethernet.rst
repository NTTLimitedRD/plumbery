Defining Ethernet networks
==========================

Each blueprint can contain one ``ethernet`` directive, like in the following exemple:

.. sourcecode:: yaml

    ethernet:
      name: myVlan1
      subnet: 192.168.20.0
      accept:
        - myVlan2

Fitting attributes
------------------

=======================  ==========  =======================================================================
Attribute                 Required    Description
=======================  ==========  =======================================================================
name                      yes         A name for the VLAN
description               no          A description of the VLAN, that can include hashtags. No default
subnet                    yes         The private IPv4 /24 network address to be used
accept                    no          A list of networks that are entitled to send traffic to this network
=======================  ==========  =======================================================================

How to allow traffic between multiple networks?
-----------------------------------------------

The ``accept`` directive is translated by plumbery into additional firewall rules automatically. This allows for easy setup, like in the following example of a 3-tier application:

.. sourcecode:: yaml

    ---

    blueprints:

      - dmz:

          ethernet:
            name: dmzNetwork
            subnet: 10.0.1.0
            accept:
              - applicationNetwork

      - application:

          ethernet:
            name: applicationNetwork
            subnet: 10.0.2.0
            accept:
              - dmzNetwork
              - databaseNetwork

      - database:

          ethernet:
            name: databaseNetwork
            subnet: 10.0.3.0
            accept:
              - applicationNetwork





