==========================
Blog server with Wordpress
==========================

Wordpress is an awesome blogging platform that is powered by Apache,
PHP and MySQL. In this tutorial we deploy a ready-to-use server.

Requirements for this use case
------------------------------

* Add a Network Domain
* Add an Ethernet network
* Deploy a Ubuntu server
* Monitor this server
* Assign a public IPv4 address
* Add address translation to ensure end-to-end IP connectivity
* Add firewall rule to accept TCP traffic on port 22 (ssh) and 80 (web)
* Install Apache2 and PHP
* Install MySQL and create a first database
* Install Wordpress

Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. literalinclude:: ../demos/wordpress.yaml
   :language: yaml
   :linenos:

You can note how SQL instructions are transmitted to the server
directly from within fittings plan.

Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

This command build fittings as per the provided plan, start the server
and bootstrap it. The last command will display the name and password
used to configure the database.

You can find the public address assigned to the web server like this:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml ping


Follow-up commands
------------------

Open a browser window and paste the public address reported by plumbery.
This should display the setup page of wordpress. Paste secrets (name and password)
that were displayed by plumbery previously. Enjoy Wordpress!

Destruction commands
--------------------

The more servers you have, the more costly it is. Would you like to stop the
invoice?

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy

