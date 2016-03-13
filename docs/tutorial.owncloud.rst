==============================
Personal storage with OwnCloud
==============================

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

.. code-block:: yaml
   :linenos:

    ---
    locationId: NA12
    regionId: dd-na

    blueprints:

      - owncloud:

          domain:
            name: OwncloudFox
            service: essentials
            ipv4: 2

          ethernet:
            name: owncloudfox.servers
            subnet: 192.168.20.0

          nodes:

            - owncloud01:

                appliance: 'Ubuntu 14'
                cpu: 2
                memory: 4
                monitoring: essentials
                glue:
                  - internet 22 80

                information:
                  - "open a browser at http://{{ node.public }}/owncloud to view it live"

                cloud-config:
                  disable_root: false
                  ssh_pwauth: true
                  bootcmd:
                    - echo "mysql-server mysql-server/root_password password {{ mysql_root.secret }}" | sudo debconf-set-selections
                    - echo "mysql-server mysql-server/root_password_again password {{ mysql_root.secret }}" | sudo debconf-set-selections
                  packages:
                    - ntp
                  runcmd:
                    - wget -nv https://download.owncloud.org/download/repositories/stable/Ubuntu_14.04/Release.key -O Release.key
                    - apt-key add - < Release.key
                    - echo "deb http://download.owncloud.org/download/repositories/stable/Ubuntu_14.04/ /" >> /etc/apt/sources.list.d/owncloud.list
                    - apt-get update
                    - apt-get install -y owncloud


**SQL password** - You can note how plumbery is asked to generate a random
password, and how this is transmitted to the server before the installation
of the sql package. For this we use the special ``bootcmd`` directive, that is
executed before the download of packages.

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
You should receive a welcome HTML page in return. The exciting stuff is to
synchronize your workstation with a mobile phone via the same owncloud instance.

Destruction commands
--------------------

The more servers you have, the more costly it is. Would you like to stop the
invoice?

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy

