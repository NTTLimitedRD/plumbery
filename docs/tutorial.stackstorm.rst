Stackstorm DevOps server
========================

In this tutorial a ready-to-use Stackstorm server is deployed.

Requirements for this use case
------------------------------

* Add a Network Domain
* Add an Ethernet network
* Deploy a Ubuntu server
* Monitor this server
* Assign a public IPv4 address
* Add address translation to ensure end-to-end IP connectivity
* Add firewall rule to accept TCP traffic on port 22 (ssh), 80 and 443 (web)
* Install StackStorm

Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. code-block:: yaml
   :linenos:

    ---
    locationId: AU10
    regionId: dd-au

    blueprints:

      - stackstorm:

          domain:
            name: StackstormFox
            service: essentials
            ipv4: auto

          ethernet:
            name: stackstorm.ethernet
            subnet: 192.168.20.0

          nodes:

            - stackstorm:

                cpu: 4
                memory: 8
                monitoring: essentials
                glue:
                  - internet 22 80 443

                information:
                  - "open a browser at https://{{ node.public }}/ to view it live"

                cloud-config:
                  disable_root: false
                  ssh_pwauth: true
                  packages:
                    - ntp
                  runcmd:
                    - curl -sSL https://raw.githubusercontent.com/DimensionDataCBUSydney/st2_dimensiondata/master/install-au.sh | sh

Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

This command will build fittings as per the provided plan, start the server
and bootstrap it.

You can find the public address assigned to the web server like this:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml information


Follow-up commands
------------------

Open a browser window and paste the public address reported by plumbery.
You should receive a login page in return.

Destruction commands
--------------------

The more servers you have, the more costly it is. Would you like to stop the
invoice?

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy

