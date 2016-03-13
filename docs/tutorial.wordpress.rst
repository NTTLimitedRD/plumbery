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

.. code-block:: yaml
   :linenos:

    ---
    locationId: EU7 # Amsterdam in Europe
    regionId: dd-eu

    blueprints:

      - wordpress:

          domain:
            name: WordpressFox
            service: essentials
            ipv4: 2

          ethernet:
            name: wordpressfox.servers
            subnet: 192.168.20.0

          nodes:

            - wordpress01:

                cpu: 2
                memory: 4
                monitoring: essentials
                glue:
                  - internet 22 80

                information:
                  - "open a browser at http://{{ node.public }}/ to view it live"
                  - "administration user name is: wpuser"
                  - "and the password when asked: {{ random.secret }}"

                cloud-config:
                  disable_root: false
                  ssh_pwauth: true
                  packages:
                    - ntp
                    - apache2
                    - mysql-server
                    - libapache2-mod-php5
                    - php5-mysql

                  write_files:

                    - path: /root/wordpress_db.sql
                      content: |
                        create database wordpress;
                        create user 'wpuser'@'localhost' identified by '{{ random.secret }}';
                        grant all privileges on wordpress.* to 'wpuser'@'localhost';
                        flush privileges;
                        drop database test;
                        drop user 'test'@'localhost';
                        flush privileges;

                  runcmd:
                    - cp -n /var/www/html/index.html /var/www/html/index.html.deprecated
                    - wget http://wordpress.org/latest.tar.gz -P /tmp/
                    - tar -zxf /tmp/latest.tar.gz -C /tmp/
                    - sudo mv /tmp/wordpress/* /var/www/html/
                    - sudo chown -R www-data:www-data /var/www
                    - mysql -e "source /root/wordpress_db.sql"
                    - mysqladmin -u root password '{{ random.secret }}'

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

