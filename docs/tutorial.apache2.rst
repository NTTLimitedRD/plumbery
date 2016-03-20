==================
Apache2 web server
==================

Ok, let's start with something simple. In this tutorial we will deploy
a basic web server with Apache2 and PHP on Linux.

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
* Change the home page

Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. code-block:: yaml
   :linenos:

    locationId: EU6 # Frankfurt in Europe
    regionId: dd-eu

    blueprints:

      - apache2:

          domain:
            name: Apache2Fox
            description: "Demonstration of a standalone apache2 web server"
            service: essentials
            ipv4: 2

          ethernet:
            name: apache2fox.servers
            subnet: 192.168.20.0

          nodes:

            - apache01:

                cpu: 1
                memory: 2

                monitoring: essentials

                glue:
                  - internet 22 80

                information:
                  - "open a browser at http://{{ node.public }}/ to view it live"

                cloud-config:

                  disable_root: false
                  ssh_pwauth: true

                  packages:
                    - ntp
                    - apache2
                    - libapache2-mod-php5

                  write_files:

                    - content: |
                        <html>
                         <head>
                          <title>Hello World</title>
                         </head>
                         <body>
                         <h1>Hello World</h1>
                            <?php echo '<p>This is a warm welcome from plumbery {{ plumbery.version }}</p>'; ?>
                         </body>
                        </html>
                      path: /var/www/html/index.php

                  runcmd:
                    - mv /var/www/html/index.html /var/www/html/index.html.deprecated

Some notes on directives used in these fittings plan:

``service: advanced`` - Dimension Data provides several flavours of Network
Domains. Here the decision is to deploy an ``advanced`` domain

``monitoring: essential`` - Automatically adds monitoring to this node after
its creation.

``ipv4: 2`` - This is to reserve some public IPv4 addresses. Here we anticipate
on the public address assigned to the web server.

``glue:`` - This directive adds connectivity to a node, either by assigning
a public IPv4 address to the Internet, or by adding network interfaces to
additional networks. With ``internet 22 80``, Plumbery assigns a public IPv4
address and adds NAT rules to the firewall. One allows SSH access, and the other
one is for web access.

``information:`` - This directive helps to document complex deployments. It can
be used to communicate instructions based on real address assignment, like in
this example.

``cloud-config`` - A list of statements that are passed to cloud-init so
that they can be applied to the node during boot sequence. In this example
we install a couple of packages, and write a new home page for this server.


Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

This command will build fittings as per the provided plan, start the server
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

