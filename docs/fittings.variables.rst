Using dynamic variables
=======================

Plumbery will set pre-defined attributes when asked, for example, a private IPv4 address to a node.
This is working great, and all you have to do for this is document such attributes in a fittings plan.

However in many situations you will handle information that is either created dynamically, or
that is declared outside a fittings plan.

Some examples:

* IPv6 addresses assigned automatically by the platform
* IPv4 addresses selected dynamically from subnets
* random password used for the setup of a MySQL server
* SSH keys to be created for a specific deployment

This is where you can use templating capabilities of plumbery directly in the fittings plan.

To illustrate the case we will consider a deployment with two nodes deployed in different data centres.
The nodes have to communicate over the IPv6 back-end infrastructure that connects all data centres
deployed by Dimension Data. In other terms, the IPv6 address of node-a has to be given to node-b, and
the IPv6 address of node-b has to be given to node-a.

As you can expect, the most straightforward implementation relies on the file /etc/hosts of both nodes.
This is the natural place where names and addresses can be mapped. In plumbery,
we would start with something like the following:

.. sourcecode:: yaml

    write_files:

        # map IPv6 addresses with names
        #
        - path: /etc/hosts
          content: |
             {{ node-a.ipv6 }}    node-a
             {{ node-b.ipv6 }}    node-b


Before the content of /etc/hosts is actually sent to the nodes, plumbery looks for
references to dynamic variables, and replaces them with actual values. For example:

.. sourcecode:: yaml

    write_files:

        # map IPv6 addresses with names
        #
        - path: /etc/hosts
          content: |
             2001:0db8:85a3:0:0:8a2e:370:7334    node-a
             2001:db8:85a3:8d3:1319:8a2e:370:7348    node-b


Dynamic variables
-----------------

Dynamic variables reflect values assigned by the cloud platform such as network addresses.

=======================  ======================  ================================================================================================
Variable                 Example                 Description
=======================  ======================  ================================================================================================
Self-name                {{ node.name }}         Name of the current node, e.g., Server1
Self private address     {{ node.private }}      Private IPv4 address, e.g., 10.11.2.3
Self public address      {{ node.public }}       Public IPv4 address, e.g., 8.9.10.11 -- requires the directive 'internet' to assign an address
Self IPv6 address        {{ node.ipv6 }}         IPv6 address defined for the node
Node private address     {{ server1.private }}   Private IPv4 address of server named server1
Node public address      {{ server1.public }}    Public IPv4 address -- requires the directive 'internet' as well
Node IPv6 address        {{ host357.ipv6 }}       IPv6 address defined for the node named host357
=======================  ======================  ================================================================================================

