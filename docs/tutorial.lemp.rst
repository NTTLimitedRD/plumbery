======================================
LEMP server (Linux, Nginx, PHP, MySQL)
======================================

This is a basic installation of a fast web server.

Requirements for this use case
------------------------------

* Add a Network Domain
* Add an Ethernet network
* Deploy a Linux server
* Monitor this server
* Assign a public IPv4 address
* Add address translation to ensure end-to-end IP connectivity
* Add firewall rule to accept TCP traffic on port 22 (ssh) and 80 (web)
* Install Nginx, PHP and MySQL
* Change the index web page and provide a PHP information page

Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. code-block:: yaml
   :linenos:

    ---

    locationId: NA12
    regionId: dd-na

    blueprints:

      - lemp:

          domain:
            name: LempFox
            service: essentials
            ipv4: 2

          ethernet:
            name: lempfox.servers
            subnet: 192.168.20.0

          nodes:

            - apache01:

                cpu: 2
                memory: 4

                monitoring: essentials
                glue:
                  - internet 22 80

                information:
                  - "open a browser at http://{{ node.public }}/ to view it live"

                cloud-config:

                  disable_root: false
                  ssh_pwauth: true
                  apt_update: true

                  packages:
                    - nginx
                    - php5-fpm
                    - php5-mysql
                    - mysql-server
                    - php5-mcrypt
                    - php5-gd
                    - php5-curl

                  write_files:

                    - path: /etc/nginx/sites-available/default
                      content: |
                          server {
                            listen 80 default_server;
                            listen [::]:80 default_server ipv6only=on;
                            root /var/www/html;
                            index index.php index.html index.htm;
                            server_name localhost;
                            location / {
                                # First attempt to serve request as file, then
                                # as directory, then fall back to displaying a 404.
                                try_files $uri $uri/ =404;
                                # Uncomment to enable naxsi on this location
                                # include /etc/nginx/naxsi.rules
                            }
                            error_page 404 /404.html;
                            error_page 500 502 503 504 /50x.html;
                            location = /50x.html {
                                root /usr/share/nginx/html;
                            }
                            location ~ \.php$ {
                                try_files $uri =404;
                                fastcgi_split_path_info ^(.+\.php)(/.+)$;
                                fastcgi_pass unix:/var/run/php5-fpm.sock;
                                fastcgi_index index.php;
                                include fastcgi.conf;
                            }
                          }

                    - path: /var/www/html/index.php
                      content: |
                        <html>
                         <head>
                          <title>Hello World</title>
                         </head>
                         <body>
                         <h1>Hello World</h1>
                            <?php echo '<p>This is a warm welcome from plumbery {{ plumbery.version }}</p>'; ?>
                            <?php echo '<p>Powered by Linux-Nginx-MySQL-PHP (LEMP)</p>'; ?>
                         </body>
                        </html>

                    - path: /var/www/html/info.php
                      content: |
                          <?php
                          phpinfo();
                          ?>
                  runcmd:
                    - mv /var/www/html/index.html /var/www/html/index.html.deprecated
                    - mkdir -p /var/www/html
                    - cp /usr/share/nginx/html/index.html /var/www/html/
                    - sed -ie "s/;cgi.fix_pathinfo=1/cgi.fix_pathinfo=0/" /etc/php5/fpm/php.ini
                    # Ensure backwards compatible with 14.04
                    - file=/etc/nginx/fastcgi.conf; if [ ! -f "$file" ]; then ln -s /etc/nginx/fastcgi_params "$file"; fi
                    - service nginx restart


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

