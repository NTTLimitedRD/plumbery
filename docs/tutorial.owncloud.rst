=============================================
How to deploy a personal cloud for your files
=============================================

OwnCloud is a web application that can store and serve content from a
centralized location, much like Dropbox. The difference is that ownCloud
allows you to host the serving software on your own machines, taking the
trust issues out of putting your personal data someone else's server.

Requirements for this use case
------------------------------

* Add a Network Domain
* Add an Ethernet network
* Deploy a Ubuntu server
* Monitor this server
* Assign a public IPv4 address
* Add address translation to ensure end-to-end IP connectivity
* Add firewall rule to accept TCP traffic on port 22 (ssh) and 80 (web)
* Install owncloud

Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. literalinclude:: ../demos/owncloud.yaml
   :language: yaml
   :linenos:


Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml build
    $ python -m plumbery fittings.yaml start
    $ python -m plumbery fittings.yaml rub

These commands will build fittings as per the provided plan, start the server
and bootstrap it.

You can find the public address assigned to the web server like this:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml ping


Follow-up commands
------------------

Open a browser window and paste the public address reported by plumbery.
You should receive a welcome HTML page in return. The exciting stuff is to
synchronize your workstation with a mobile phone via the same owncloud instance.

Destruction commands
--------------------

The more servers you have, the more costly it is. Would you like to stop the
invoice?

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy

