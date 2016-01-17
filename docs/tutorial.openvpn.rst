===============
OpenVPN gateway
===============

This is a basic installation of a VPN gateway, directly in the cloud.

Requirements for this use case
------------------------------

* Add a Network Domain
* Add an Ethernet network
* Deploy a CentOS server
* Monitor this server
* Assign a public IPv4 address
* Add address translation to ensure end-to-end IP connectivity
* Add firewall rule to accept TCP traffic on port 22 (ssh) and 943 (openvpn)
* Install OpenVPN
* Change the password of the openvpn account

Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. literalinclude:: ../demos/openvpn.yaml
   :language: yaml
   :linenos:


Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

These commands will build fittings as per the provided plan, start the server
and bootstrap it.

You can find the public address assigned to the web server like this:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml ping


Follow-up commands
------------------

Open a browser window and paste the public address reported by plumbery.
You should receive a welcome HTML page in return.

Destruction commands
--------------------

The more servers you have, the more costly it is. Would you like to stop the
invoice?

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy

