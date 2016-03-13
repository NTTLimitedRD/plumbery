====================================
The master plan to conquer the world
====================================

The goal of GigaFox is to deploy a global infrastructure involving
multiple resources spread in different regions and connected to each other.
Their fittings plan is the biggest of all.

Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. literalinclude:: ../demos/fittings.yaml
   :language: yaml
   :linenos:

Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml build
    $ python -m plumbery fittings.yaml start
    $ python -m plumbery fittings.yaml prepare

These commands will build fittings as per the provided plan, and start
the server as well. Look at messages displayed by plumbery while it is
working, so you can monitor what's happening.

Destruction commands
--------------------

Cloud computing has a hard rule. Any resource has a cost, be it used or not.
At the end of every session, you are encouraged to destroy everything.
Hopefully, plumbery is making this really simple:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy

