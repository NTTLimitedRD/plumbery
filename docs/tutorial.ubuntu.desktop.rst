========================
Ubuntu graphical desktop
========================

While Linux practitioners commonly use the command line to play with servers,
they are cases where a good graphical interface is making life far easier.
In this tutorial a Ubuntu server is deployed, then a desktop is added, then
remote graphical access is provided with VNC.

We also want to add a password to the VNC server, and to tunnel the traffic
in SSH to prevent eyesdropping.

Requirements for this use case
------------------------------

* Add a Network Domain
* Add an Ethernet network
* Deploy a Ubuntu server
* Monitor this server
* Assign a public IPv4 address
* Add address translation to ensure end-to-end IP connectivity
* Add firewall rule to accept TCP traffic on port 22 (ssh)
* Install Ubuntu gnome-based desktop
* Install VNC server
* Configure VNC as a service

Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. literalinclude:: ../demos/ubuntu.desktop.yaml
   :language: yaml
   :linenos:

Some interesting remarks on this fittings plan:

* The password used by VNC server is normally entered interactively. Here
  the package ``expect`` has been added, with a little script, to automate
  this interactivity. This is a very powerful mechanism that can be useful
  in multiple situations.

* The VNC server is installed as an ordinary service via an additional command
  in `/etc/init.d/` and  with `update-rc.d`

* The ``information:`` directive provides comprehensive instructions to
  finalise the setup. This is displayed at the end of the command ``deploy``.
  It can also be retrieved unattended with the command ``information``.


Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

This command will build fittings as per the provided plan, start the server
and bootstrap it.

Follow-up commands
------------------

You can find instructions to connect, including IP addresses to use, like this:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml information

Of course, you need a VNC viewer on your computer to make it work. As a starting
point you can attempt to enter the following URL in a browser window::

    vnc://127.0.0.1:5901

Destruction commands
--------------------

The more servers you have, the more costly it is. Would you like to stop the
invoice?

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml dispose

