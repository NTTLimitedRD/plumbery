========================================
iTop Community, to manage your IT assets
========================================

This use case will be useful to companies looking for an open source solution
that fosters ITIL best practices: `iTop Community, from Combodo`_.

.. image:: tutorial.itop.png


Requirements for this use case
------------------------------

There are a number of actions involved in the overall deployment, and plumbery
will assist to orchestrate all of them, except the online setup of iTop:

* Add a Network Domain
* Add an Ethernet network
* Deploy a Ubuntu server
* Monitor this server
* Assign a public IPv4 address
* Add address translation to ensure end-to-end IP connectivity
* Add firewall rule to accept TCP traffic on port 22 (ssh) and 80 (web)
* Update `etc/hosts` to bind addresses to host names
* Manage keys to suppress passwords in SSH connections
* Download multiple packages, including Apache, PHP, MySQL
* Install MySQL
* Download and install iTop

Fittings plan
-------------

`Download this fittings plan`_ if you want to hack it for yourself. This is part of `the demonstration
directory of the plumbery project`_ at GitHub. Alternatively, you can copy the
text below and put it in a text file named ``fittings.yaml``.

.. literalinclude:: ../demos/itop.yaml
   :language: yaml
   :linenos:


Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

This command will build fittings as per the provided plan, and start
server as well. Look at messages displayed by plumbery while it is
working, so you can monitor what's happening.

Follow-up commands
------------------

At the end of the deployment, plumbery will display on screen some instructions
to help you move forward. You can ask plumbery to display this information
at any time with the following command:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml information

Final step is to connect to iTop in a web browser, and to complete the setup
online.

Destruction commands
--------------------

To destroy everything and stop the bill you would do:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml dispose


.. _`iTop Community, from Combodo`: http://www.combodo.com/itop-193
.. _`Download this fittings plan`: https://github.com/bernard357/plumbery/blob/master/demos/mqtt.pinger.swarm.yaml
.. _`the demonstration directory of the plumbery project`: https://github.com/bernard357/plumbery/tree/master/demos