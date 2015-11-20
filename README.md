# plumbery

Are you looking for a cloud plumber? We hope that this one will be useful to you

## Cloud automation at Dimension Data with Apache Libcloud

This project started in response to a very common issue. How to automate the creation, the handling, and the destruction of about 10 to 50 virtual servers easily?

The simple toolbox here is based on a central description of servers, documented in a text file in YAML. If you do not know YAML yet, don't be afraid, this may be the most simple and user-friendly language for infrastructure managers. Have a look at the sample fittings.yaml that is coming with plumbery to get an idea.

Then very simple Python code is used to act on the infrastructure. For example you can build the entire set of resources described in YAML interactively, in the Python interpreter:

"""bash
from plumbery import Plumbery

plumbery = Plumbery()
plumbery.build_all_blueprints()
"""

This will load the YAML file, parse it, and call the cloud API to make it happen. Relax, and grab some coffee, while plumbery adds network domains, Ethernet networks, and servers as per your specifications.

Then you can start all nodes with a single statement as well:

"""plumbery.start_all_nodes()
"""

Now you can concentrate on important things, connect remotely to the nodes, play with them, run different tests, etc. At the end of the game, you would just have to stop all servers and destroy them as per following statements:

"""plumbery.stop_all_nodes()
plumbery.destroy_all_nodes()
"""

## How do I handle a subset of my resources?

In plumbery the full fittings is split in multiple blueprints. The most natural way to think about this is to conceive services with group of servers. For example, the blueprint "sql" is actually a cluster of nodes plugged into the same network. Look at the sample fittings.yaml file to get an idea of what you can put in a blueprint.

Then you can handle a single blueprint independently from the others:

"""plumbery.build_blueprint('sql')
plumbery.start_nodes('sql')
plumbery.stop_nodes('sql')
plumbery.destroy_nodes('sql')
"""

## Great, how to install plumbery on my machine?

Everything here is based on Python and on open source software, so it should not be too difficult to most people with some experience of Linux.

The first thing to install is Python itself, then you have to clone Apache Libcloud, and then plumbery. Voila!
