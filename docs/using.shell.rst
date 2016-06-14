Using plumbery from the command-line
====================================

Move first to the directory that contains your fittings plan, and then run:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

Plumbery will load ``fittings.yaml``, then build all blueprints there.

As you can expect, plumbery can be invoked through the entire life cycle of
your fittings:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml build
    $ python -m plumbery fittings.yaml start
    $ python -m plumbery fittings.yaml prepare

    ... nodes are up and running here ...

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy

The table below presents succinctly all actions that are supported by plumbery.

  ============  =============================================================
  Action        Description
  ============  =============================================================
  deploy        equivalent to: build + configure + start + prepare
  dispose       equivalent to: stop + destroy
  build         create network domains, networks, and nodes
  configure     adds public IP addresses, NAT and firewall rules
  start         start nodes
  prepare       contextualise nodes via ssh and cloud-init
  information   display information put in fittings plan
  inventory     produce an inventory of all assets deployed
  ansible       allow ansible to handle nodes and groups deployed by plumbery
  ping          check the status of nodes and display network addresses
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


When you are not sure of directives put in fittings plan, you can ask plumbery
for a dry-run. Use the -s swiftch to keep it safe:

.. sourcecode:: bash

    $ python -m plumbery <your_various_args> -s

If some strange behaviour occurs, and you cannot understand what is happening,
then you can use the debug option to get more information:

.. sourcecode:: bash

    $ python -m plumbery <your_various_args> -d


Of course the switches -s and -d can be combined if needed.


.. _`YAML`: https://en.wikipedia.org/wiki/YAML
.. _`available on PyPi`: https://pypi.python.org/pypi/plumbery
.. _`Plumbery package at PiPy`: https://pypi.python.org/pypi/plumbery
.. _`Plumbery repository at GitHub`: https://github.com/bernard357/plumbery
.. _`download the reference fittings plan`: https://raw.githubusercontent.com/bernard357/plumbery/master/demos/fittings.yaml


