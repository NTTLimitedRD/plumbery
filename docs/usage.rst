======================
Infrastructure as code
======================

Plumbery is an open-source project that supports a strange paradigm.
Infrastructure should be handled like code. For people who have relied for years
on the power of physical stuff, this may be a shock. So let's repeat it again.
When interesting resources have been virtualised and accessed remotely then
suddenly infrastructure managers have new challenges. Infrastructure should be
treated like code is. A lot of best practices are coming with this paradigm.

And issues, too. Becoming a trusted Ops --yes, the end of DevOps-- is not so
easy. How to deal with developers while being not a software developer? Well,
this is exactly why Plumbery has been developed.

Actually we believe that every infrastructure manager should have enough skills
to use Plumbery on his own. Here we are referring to tasks like the following:

* open and edit textual files
* understand and modify configuration files
* connect to a Linux server via ssh
* set environment variables
* run a command from the prompt line
* execute a python program

One day in the life of an ordinary infrastructure manager
---------------------------------------------------------

This project started in response to a very common issue. How to accelerate the
creation, the handling, and the destruction of up to 60 virtual servers
easily? The purpose here is not to supplement Chef, Puppet, and other smart
configuration management that already exist. Our ambition is limited to the
industrialisation of the underlying virtualised iron. No more, no less.

The Plumbery toolbox is based on a central description of servers,
documented in a text file in YAML. If you do not know YAML yet, don't be
afraid, this may be the most simple and user-friendly language for
infrastructure managers. Have a look at the sample ``fittings.yaml``
that is coming with plumbery to get an idea.

Then very simple Python code is used to act on the infrastructure. For example
you can build the entire set of resources described in the fittings plan
directly in the python interpreter:

.. sourcecode:: python

    >>>from plumbery.engine import PlumberyEngine
    >>>engine = PlumberyEngine('fittings.yaml')
    >>>engine.build_all_blueprints()
    ...

This will load the YAML file, parse it, and call the cloud API to make it
happen. Relax, and grab some coffee while plumbery adds network domains,
Ethernet networks, and servers as per your specifications. The engine may plumb
at various data centres spread on Earth, thanks to the power of Apache Libcloud.

Then you can start all nodes with a single statement as well:

.. sourcecode:: python

    >>>engine.start_all_nodes()
    ...


Now you can concentrate on important things, connect remotely to the nodes,
play with them, run different tests, etc. At the end of the game, you would
just have to stop all servers and destroy them as per following statements:

.. sourcecode:: python

    >>>engine.stop_all_nodes()
    ...
    >>>engine.destroy_all_nodes()
    ...


Infrastructure as code at Dimension Data with Apache Libcloud
-------------------------------------------------------------

If infrastructure should be handled like code, then your first task is to
document a target deployment into a text file. In the context of Plumbery, this
is called the fittings plan, and it is usually put into a file
named ``fittings.yaml``.

With that in hands, you can then use Plumbery to act on the infrastructure and
on nodes. The engine has built-in code to cover the full life cycle:

* build the infrastructure and configure it
* build nodes
* start nodes
* polish nodes -- this is to say that some processing is applied to each node
* stop nodes
* destroy nodes
* destroy the infrastructure and release all resources

How do I describe fittings plan?
--------------------------------

The fittings plan is expected to follow YAML specifications, and it
must have multiple documents in it. The first document provides
general configuration parameters for the engine. Subsequent documents
describe the various locations for the fittings.

An example of a minimum fittings plan:

.. sourcecode:: yaml

    ---
    safeMode: False
    ---
    # Frankfurt in Europe
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

In this example, the plan is to deploy a single node in the data centre
at Frankfurt, in Europe. The node `myServer` will be placed in a
network named `myVLAN`, and the network will be part of a network
domain acting as a virtual data centre, `myDC`. The blueprint has a
name, `myBluePrint`, so that it can be handled independently from
other blueprints.

(help needed here to present YAML structure expected by Plumbery)

In the ``demos`` directory that is coming with Plumbery you will find a
reference ``fittings.yaml`` file, plus many programs that are using Plumbery.

How do I handle a subset of cloud resources?
--------------------------------------------

You are right to ask. A common use case is the immediate creation of a new
group of servers for some developer. You would not like this to interfere
with existing servers. On the other hand, you may really want to destroy a
group of unused servers that just add to the monthly invoices.

In plumbery the full fittings plan is split in multiple blueprints, and you can
handle each of them separately. The most natural way to think about this is to
conceive services as group of servers. For example, the blueprint ``docker`` is
actually a cluster of nodes plugged into the same network. Look at the sample
``fittings.yaml`` file to get an idea of what you can put in a blueprint.

Then you can handle a single blueprint independently from the others:

.. sourcecode:: python

    >>>plumbery.build_blueprint('docker')
    ...
    >>>plumbery.start_nodes('docker')
    ...
    >>>plumbery.stop_nodes('docker')
    ...
    >>>plumbery.destroy_nodes('docker')
    ...

Also, a blueprint can be spread across multiple data centres, and this is the
very basis of fault tolerant services. For example for ``sql``, this blueprint
could feature a master SQL database server at one data centre, and a slave SQL
database at another data centre. In that case, plumbery will connect separately
to each data centre and to the dirty job to make you happy. Look at the snippet
below to get a better idea of how simple this can be.

.. sourcecode:: yaml

    ---
    # Amsterdam in Europe
    locationId: EU7
    regionId: dd-eu

    blueprints:

      # primary sql server
      - sql:
          domain:
          ethernet:
          nodes:
            - masterSQL:
                description: '#sql #vdc1 #primary'
                appliance: 'RedHat 6 64-bit 4 CPU'

    ---
    # Frankfurt in Europe
    locationId: EU6
    regionId: dd-eu

    blueprints:

      # secondary sql server
      - sql:
          domain:
          ethernet:
          nodes:
            - slaveSQL:
                description: '#sql #vdc2 #secondary'
                appliance: 'RedHat 6 64-bit 4 CPU'

