==============
Node.js server
==============

Are you more familiar with javascript? Ok, let's continue with a
different flavour of web site, powered by node.js.

Requirements for this use case
------------------------------

* Add a Network Domain
* Add an Ethernet network
* Deploy a Ubuntu server
* Monitor this server
* Assign a public IPv4 address
* Add address translation to ensure end-to-end IP connectivity
* Add firewall rule to accept TCP traffic on port 22 (ssh) and 80 (web)
* Install Node.js
* Install a javascript to serve the home page

Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. code-block:: yaml
   :linenos:

    ---
    locationId: EU6 # Frankfurt in Europe
    regionId: dd-eu

    blueprints:

      - nodejs:

          domain:
            name: NodejsFox
            service: essentials
            ipv4: 2

          ethernet:
            name: nodejsfox.servers
            subnet: 192.168.20.0

          nodes:
            - nodejs02:

                cpu: 2
                memory: 8
                monitoring: essentials
                glue:
                  - internet 22 8080

                information:
                  - "open a browser at http://{{ node.public }}:8080/ to view it live"

                cloud-config:
                  disable_root: false
                  ssh_pwauth: True

                  bootcmd:
                    - "curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -"

                  packages:
                    - ntp
                    - git
                    - nodejs

                  write_files:

                    - path: /root/hello.js
                      content: |
                        var http = require('http');
                        http.createServer(function (req, res) {
                          res.writeHead(200, {'Content-Type': 'text/html'});
                          res.end('<h2>Hello World</h2>\nThis is a warm welcome from plumbery {{ plumbery.version }}');
                        }).listen(8080, '0.0.0.0');
                        console.log('Server running at http://{{ node.public }}:8080/');

                  runcmd:
                    - npm install pm2 -g
                    - rm /etc/init.d/pm2-init.sh
                    - pm2 startup
                    - pm2 start /root/hello.js
                    - pm2 save

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
You should receive a welcome page in return.

Destruction commands
--------------------

The more servers you have, the more costly it is. Would you like to stop the
invoice?

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy

