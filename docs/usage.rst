======================
Infrastructure as code
======================

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
infrastructure managers. Have a look at the sample ``fittings.yaml`
that is coming with plumbery to get an idea.

Then very simple Python code is used to act on the infrastructure. For example
you can build the entire set of resources described in the fittings plan
directly in the python interpreter:

.. sourcecode:: python

    from plumbery.engine import PlumberyEngine

    engine = PlumberyEngine('fittings.yaml')
    engine.build_all_blueprints()

This will load the YAML file, parse it, and call the cloud API to make it
happen. Relax, and grab some coffee while plumbery adds network domains,
Ethernet networks, and servers as per your specifications. The engine may plumb
at various data centres spread on Earth, thanks to the power of Apache Libcloud.

Then you can start all nodes with a single statement as well:

.. sourcecode:: python

    plumbery.start_all_nodes()


Now you can concentrate on important things, connect remotely to the nodes,
play with them, run different tests, etc. At the end of the game, you would
just have to stop all servers and destroy them as per following statements:

.. sourcecode:: python

    plumbery.stop_all_nodes()
    plumbery.destroy_all_nodes()


In other terms, Plumbery is an open-source project that supports the
paradigm that infrastructure should be handled like code. Of course, you can
use Plumbery without transforming yourself to a software developer.

Every infrastructure manager should have enough skills to use Plumbery on his
own. Here we are referring to tasks like the following:

* open and edit textual files
* understand and modify configuration files
* connect to a Linux server via ssh
* set environment variables
* run a command from the prompt line
* execute a python program

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

In the ``demos`` directory that is coming with Plumbery you will find a
reference ``fittings.yaml`` file, plus many programs that are using Plumbery.

(help needed here to present YAML structure expected by Plumbery)

How do I handle a subset of cloud resources?
--------------------------------------------

You are right to ask. A common use case is the immediate creation of a new
group of servers for some developer. You would not like this to interfere
with existing servers. On the other hand, you may really want to destroy a
group of unused servers that just add to the monthly invoices.

In plumbery the full fittings plan is split in multiple blueprints, and you can
handle each of them separately. The most natural way to think about this is to
conceive services as group of servers. For example, the blueprint ``sql`` is
actually a cluster of nodes plugged into the same network. Look at the sample
``fittings.yaml`` file to get an idea of what you can put in a blueprint.

Then you can handle a single blueprint independently from the others:

.. sourcecode:: python

    plumbery.build_blueprint('sql')
    plumbery.start_nodes('sql')
    plumbery.stop_nodes('sql')
    plumbery.destroy_nodes('sql')

Also, a blueprint can be spread across multiple data centres, and this is the
very basis of fault tolerant services. For example for ``sql``, this blueprint
could feature a master SQL database server at one data centre, and a slave SQL
database at another data centre. In that case, plumbery will connect separately
to each data centre and to the dirty job to make you happy. Look at the snippet
below to get a better idea of simple this can be.

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

