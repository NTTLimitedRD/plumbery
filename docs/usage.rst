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
documented in a text file in `YAML`_. If you do not know YAML yet, don't be
afraid, this may be the most simple and user-friendly language for
infrastructure managers. Have a look at the sample ``fittings.yaml``
that is coming with plumbery to get an idea.

Then very simple Python code is used to act on the infrastructure. For example
you can build the entire set of resources described in the fittings plan
directly from the command line:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

This will load the YAML file, parse it, and call the cloud API to make it
happen. Relax, and grab some coffee while plumbery adds network domains,
Ethernet networks, and servers as per your specifications. The engine may plumb
at various data centres spread on Earth, thanks to the power of Apache Libcloud.
Nodes will be started and contextualise with cloud-init directives as well.

Now you can concentrate on important things, connect remotely to the nodes,
play with them, run different tests, etc. At the end of the game, you would
just have to stop all servers and destroy them as per following statement:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml dispose


Infrastructure as code at Dimension Data with Apache Libcloud
-------------------------------------------------------------

If infrastructure should be handled like code, then your first task is to
document a target deployment into a text file. In the context of Plumbery, this
is called the fittings plan, and it is commonly put into a file
named ``fittings.yaml``.

With that in hands, you can then ask Plumbery to act on the infrastructure and
on nodes. The engine has built-in code to cover the full life cycle:

* deploy the infrastructure and configure it
* build nodes
* start nodes
* polish nodes -- this is to say that some processing is applied to each node
* stop nodes
* destroy nodes
* dispose the infrastructure and release all resources

How do I describe fittings plan?
--------------------------------

The fittings plan is written in YAML, and it
must have multiple documents in it. The first document provides
general configuration parameters for the engine. Subsequent documents
describe the various locations for the fittings.

An example of a minimum fittings plan:

.. sourcecode:: yaml

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

Run Plumbery from the command line
----------------------------------

As exposed before, plumbery can be run directly from the command line.
Move first to the directory that contains your fittings plan, and then run:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

Plumbery will load ``fittings.yaml``, then build all blueprints there.

As you can expect, plumbery can be invoked through the entire life cycle of
your fittings:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml build
    $ python -m plumbery fittings.yaml start
    $ python -m plumbery fittings.yaml polish

    ... nodes are up and running here ...

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy

The table below presents succinctly all actions that are supported by plumbery.

  ============  =============================================================
  Action        Description
  ============  =============================================================
  deploy        equivalent to: build + spit + start + rub
  dispose       equivalent to: stop + destroy
  build         create network domains, networks, and nodes
  spit          adds public IP addresses, NAT and firewall rules
  start         start nodes
  rub           contextualise nodes via ssh and cloud-init
  information   display node information put in fittings plan
  stop          stop nodes
  wipe          destroy only nodes
  destroy       destroy nodes and other resources
  polish        apply all polishers configured in fittings plan
  secrets       display secrets such as random passwords, etc.
  ============  =============================================================


How do I handle a subset of cloud resources?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml build docker
    $ python -m plumbery fittings.yaml build sql

    ... and then later ...

    $ python -m plumbery fittings.yaml destroy sql
    $ python -m plumbery fittings.yaml build mongodb

How to apply a specific polisher?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To apply a polisher just mention its name on the command line. For example,
if fittings plan has a blueprint for nodes running Docker, then you may
use the polisher ``rub`` to install Docker itself at each node:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml build docker
    $ python -m plumbery fittings.yaml start docker
    $ python -m plumbery fittings.yaml rub docker

    ... Docker is up and running at multiple nodes ...

If you create a new polisher and put it in the directory ``plumbery\polishers``,
then it will become automatically available:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml my_special_stuff

How to plumb only at a selected location?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default Plumbery looks at every location mentioned in fittings plan.
Sometimes you may want to limit actions performed to some locations.
For this, mention the name of the target location, prefixed by ``@``.
As an example, here would be the command to build SQL servers only at NA12:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml build sql @NA12


How to get help from the command line?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. sourcecode:: bash

    $ python -m plumbery -h


If some strange behaviour occurs, and you cannot understand what is happening,
then you can use the debug option to get more information:

.. sourcecode:: bash

    $ python -m plumbery <your_various_args> -d


Use Plumbery as a python library
--------------------------------

Since Plumbery is easy to load, you can use it interactively like in the
following example:

.. sourcecode:: python

    >>>from plumbery.engine import PlumberyEngine
    >>>PlumberyEngine('fittings.yaml').build_blueprint('beachhead control')
    ...

If you are writing some code using Plumbery as a library, you would import
the engine and use it, as with any other python module. For example:

.. sourcecode:: python

    from plumbery.engine import PlumberyEngine

    engine = PlumberyEngine('fittings.yaml')
    engine.build_blueprint('docker')
    engine.start_blueprint('docker')
    engine.polish_blueprint('docker', 'rub')


To go deeper into the code itself, you could have a look at the documentation
extracted from the code, at :ref:`modindex` and :ref:`genindex`. And of course
the source code is available on-line, check the `Plumbery repository at GitHub`_.


.. _`YAML`: https://en.wikipedia.org/wiki/YAML
.. _`available on PyPi`: https://pypi.python.org/pypi/plumbery
.. _`Plumbery package at PiPy`: https://pypi.python.org/pypi/plumbery
.. _`Plumbery repository at GitHub`: https://github.com/bernard357/plumbery
.. _`download the reference fittings plan`: https://raw.githubusercontent.com/bernard357/plumbery/master/demos/fittings.yaml


