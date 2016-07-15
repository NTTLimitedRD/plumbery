How to connect plumbery to remote nodes?
========================================

For most of the infrastructure plumbery interacts with the API endpoint. This is
how domains, networks, and nodes are deployed. This is also how network and security directives are configured.

Beyond that point, there is a need for plumbery to interact directly with the nodes. For example,
to pass commands over ssh. Or to bootstrap nodes with cloud-init. In such situations there
is a need for direct connectivity between the machine that is running plumbery and some target node.

Connect over public Internet
----------------------------

When a node has been assigned a public IPv4 address then plumbery just uses it. So the easiest way
to ensure such connectivity is to use ``glue:`` as in following example:

.. sourcecode:: yaml

    blueprints:

      - myBluePrint:

          ethernet:
            name: myNetwork
            subnet: 10.1.0.0

          nodes:

            - myServer:

                glue:
                  - internet 22

With this setup the node myServer is becoming reachable over ssh. This can be used directly by
plumbery or by a human being for remote administration.

Connect over IPv6
-----------------

If target node has not been assigned a public IPv4 address, then plumbery looks for IPv6 end-to-end
connectivity. This can only happen if the machine that is running plumbery has a routable IPv6 address for itself.

For example, if you run plumbery on a server in some MCP, it will get an IPv6 address automatically.
For the provision of end-to-end IPv6 connectivity there is a need to add a firewall rule.

For example, if the plumbery machine has been deployed on ``plumberyNetwork``, you could use following directives:

.. sourcecode:: yaml

    blueprints:

      - myBluePrint:

          ethernet:
            name: myNetwork
            subnet: 10.1.0.0
            accept:

              # accept traffic from plumbery node
              #
              - plumberyNetwork

          nodes:
            - myServer:


Connect over private IPv4
-------------------------

In the case where the target node has no public IPv4 address, and plumbery has no IPv6 address, there is a high risk
that end-to-end connectivity cannot be achieved.

A simple strategy could be that plumbery just tries to connect over ssh and complains eventually. However, this heuristic
involves very long time out delays, and therefore it is very inefficient with a significant number of nodes.

At some point it has been decided to allow only explicit connectivity in such situation. The directive ``beachhead:`` contains
a list of private IPv4 addresses that are eligible for remote connectivity.

For example:

.. sourcecode:: yaml

    # the node running plumbery has to be configured with this address
    #
    beachhead: 10.1.0.121

    blueprints:

      - myBluePrint:

          ethernet:
            name: myNetwork
            subnet: 10.1.0.0

          nodes:
            - myServer:

                cloud-config:
                  ...

