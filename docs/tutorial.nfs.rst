==============================
NFS over ipv6 back-end network
==============================

In this tutorial a NFS server is deployed at one data centre, and
a NFS client is deployed at another data centre. The infrastructure and the
nodes are configured to talk to each other over the secured ipv6 back-bone
that ties all MCP together.

Requirements for this use case
------------------------------

* Add a Network Domain at each data centre
* Add an Ethernet network at each data centre
* Allow IPv6 traffic between the two networks
* Deploy a Ubuntu server at each data centre
* Monitor these servers
* Assign a public IPv4 address to each server
* Add address translation to IPv4 connectivity from the Internet
* Add firewall rule to accept TCP traffic on port 22 (ssh)
* Add ipv6 addresses to `/etc/hosts` for easy handling
* Install NFS back-end software on server node
* Install NFS client software on client node
* At the client node, change `/etc/fstab` to mount NFS volume automatically
* From the client node, write a `hello.txt` to the server

Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. literalinclude:: ../demos/nfs.yaml
   :language: yaml
   :linenos:

Some interesting remarks on this fittings plan:

**IPv6 connectivity** - In this case we can see that network names and
private IPv4 subnets are exactly the same at both data centres. In other terms,
we don't need IPv4 to be routable across the two locations. We use IPv6 instead,
and plumbery helps to orchestrate the long addresses that are coming with this
protocol.

**etc/hosts** - The update of `etc/hosts` is made by a script in AWK language.
The script is built dynamically by plumbery, based on actual addresses assigned
to nodes. Since each data centre is described in a separate YAML document of
the fittings plan, there is a special syntax to designate remote networks and
nodes. At `AU10`, the remote network is designated by `AU11::nfsfox.servers`
and the NFS client by `AU11::nfsClient`. This is creating name spaces that can
be geographically consistent across global deployments.

**etc/fstab** - On the client side there is an example of AWK script to modify `etc/fstab`
dynamically. Therefore, if the node is rebooted it will reconnect
automatically.

Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

This command will build fittings as per the provided plan, start the server
and bootstrap it.

Follow-up commands
------------------

You can find instructions to connect, including IP addresses to use, like this:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml information

The best is to go to the NFS server via ssh, and to read the file written by
the NFS client in `/var/nfs`.

Destruction commands
--------------------

The more servers you have, the more costly it is. Would you like to stop the
invoice?

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml dispose

