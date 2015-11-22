# plumbery

Are you looking for a cloud plumber? We hope that this one will be useful to you

## Cloud automation at Dimension Data with Apache Libcloud

This project started in response to a very common issue. How to automate the creation, the handling, and the destruction of about 10 to 50 virtual servers easily? The purpose here is not to supplement Chef, Puppet, and other smart configuration management that already exist. Our ambition is limited to the industrialisation of the underlying virtualised iron. No more, no less.

The simple toolbox here is based on a central description of servers, documented in a text file in YAML. If you do not know YAML yet, don't be afraid, this may be the most simple and user-friendly language for infrastructure managers. Have a look at the sample ``fittings.yaml`` that is coming with plumbery to get an idea.

Then very simple Python code is used to act on the infrastructure. For example you can build the entire set of resources described in YAML interactively, in the Python interpreter:

```python
from plumbery.engine import PlumberyEngine

plumbery = PlumberyEngine('fittings.yaml')
plumbery.build_all_blueprints()
```

This will load the YAML file, parse it, and call the cloud API to make it happen. Relax, and grab some coffee, while plumbery adds network domains, Ethernet networks, and servers as per your specifications. The engine may plumb at various data centres spread on Earth, thanks to the power of Apache Libcloud.

Then you can start all nodes with a single statement as well:

```python
plumbery.start_all_nodes()
```

Now you can concentrate on important things, connect remotely to the nodes, play with them, run different tests, etc. At the end of the game, you would just have to stop all servers and destroy them as per following statements:

```python
plumbery.stop_all_nodes()
plumbery.destroy_all_nodes()
```

If you are reluctant to use the Python interpreter, you may prefer to use the ready-to-use scripts provided with plumbery. For example, in a shell box, type the following command to build all resources:

    $ python build_all_blueprints.py

Look at the content of the ``demos``directory to find other similar examples that you may find useful.

## How do I handle a subset of cloud resources?

You are right to ask. A common use case is the immediate creation of a new group of servers for some developer. You would not like this to interfere with existing servers. On the other hand, you may really want to destroy a group of unused servers that just add to the monthly invoices.

In plumbery the full fittings is split in multiple blueprints, and you can handle each of them separately. The most natural way to think about this is to conceive services as group of servers. For example, the blueprint ``sql`` is actually a cluster of nodes plugged into the same network. Look at the sample ``fittings.yaml`` file to get an idea of what you can put in a blueprint.

Then you can handle a single blueprint independently from the others:

```python
plumbery.build_blueprint('sql')
plumbery.start_nodes('sql')
plumbery.stop_nodes('sql')
plumbery.destroy_nodes('sql')
```

Also, a blueprint can be spread across multiple data centres, and this is the very basis of fault tolerant services. For example for ``sql``, this blueprint could feature a master SQL database server at one data centre, and a slave SQL database at another data centre. In that case, plumbery will connect separately to each data centre and to the dirty job to make you happy. Look at the snippet below to get a better idea of simple this can be.

```yaml
---
# Amsterdam in Europe
locationId: EU7
regionId: dd-eu

# fittings consist of multiple blueprints
blueprints:

  # primary sql server
  - sql:
      domain:
        name: VDC2
      ethernet:
        name: data
        subnet: 10.0.3.0
      nodes:
        - masterSQL:
            description: 'SQL #vdc2 #primary'
            appliance: 'RedHat 6 64-bit 4 CPU'

---
# Frankfurt in Europe
locationId: EU6
regionId: dd-eu

# fittings consist of multiple blueprints
blueprints:

  # secondary sql server
  - sql:
      domain:
        name: VDC1
      ethernet:
        name: data
        subnet: 10.0.3.0
      nodes:
        - slaveSQL:
            description: 'SQL #vdc1 #secondary'
            appliance: 'RedHat 6 64-bit 4 CPU'

```

## Great, how to install plumbery on my machine?

Everything here is based on Python and on open source software, so it should not be too difficult to most people with some experience of Linux, unix and the like.

The first thing to install is Python itself, then you have to clone Apache Libcloud, and then plumbery.
