====================================
The master plan to conquer the world
====================================

The goal of GigaFox is to deploy a global infrastructure involving
multiple resources spread in different regions and connected to each other.
Their fittings plan is the biggest of all.

Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. code-block:: yaml
   :linenos:

    ---

    polishers:
      - ansible:
          reap: gigafox_ansible.yaml
      - inventory:
          reap: gigafox_inventory.yaml
      - rub:
          key: ~/.ssh/id_rsa.pub
          reap: gigafox_rubs.yaml

    # each facility is described separately
    ---
    # Santa Clara - secondary site in USA
    locationId: NA12
    regionId: dd-na

    rub:
      - beachhead: 10.10.10.9
      - beachhead: 10.10.10.10

    basement: beachhead

    blueprints:

      # root resources
      - beachhead:
          domain: &domain
            name: Gigafox
            description: '#us #primary'
            service: advanced
            ipv4: 8
          ethernet: &control
            name: gigafox.control
            description: '#us #ops'
            subnet: 10.0.0.0
            destroy: never
          nodes:
            - beachhead:
                description: '#beachhead #us #ops'
                glue:
                  - internet 22
                running: always
                monitoring: essentials
                cloud-config:
                  disable_root: false
                  ssh_pwauth: True
                  packages:
                    - python-pip
                    - python-dev
                    - git
                  runcmd:
                    - pip install -e git+https://git-wip-us.apache.org/repos/asf/libcloud.git@trunk#egg=apache-libcloud
                    - pip install -e git+https://github.com/bernard357/plumbery.git#egg=plumbery

      # management, administration, and monitoring
      - control:
          domain: *domain
          ethernet: *control
          nodes:
            - stackstorm:
                description: '#stackstorm #us #ops'
                glue:
                  - internet 22 80 443
                running: always
                monitoring: essentials
                cloud-config:
                  disable_root: false
                  ssh_pwauth: True
                  runcmd:
                    - curl -sSL https://raw.githubusercontent.com/DimensionDataCBUSydney/st2_dimensiondata/master/install-eu.sh | sh
            - scom:
                description: 'Microsoft System Center Operation Manager #scom #us #ops'
                appliance: 'Win2012 R2 Std 4 CPU'
                monitoring: essentials

      # workloads dedicated to source code and related
      - source:
          domain: *domain
          ethernet:
            name: gigafox.source
            description: '#us #dev'
            subnet: 10.1.0.0
            destroy: never
          nodes:
            - gitlab:
                description: '#gitlab #us #dev'
                glue:
                  - internet 80 443
                  - gigafox.control
                monitoring: essentials

      # workloads dealing directly with end-user devices
      - web:
          domain: *domain
          ethernet: &bastion
            name: gigafox.web
            description: '#us'
            subnet: 10.2.0.0
            accept:
              - gigafox.control
            destroy: never
          nodes:
            - web[1..2]_na12:
                description: '#apache #us #primary'
                cpu: 4 2 highperformance
                memory: 8
                disks:
                  - 1 500 standard
                  - 2 100
                glue:
                  - internet 22 80 443
                monitoring: essentials
                cloud-config:
                  disable_root: false
                  ssh_pwauth: True
                  packages:
                    - apache2
                    - mysql-server
                    - libapache2-mod-php5
                    - php5-mysql
                  runcmd:
                    - "rm /var/www/index.html"
                  write_files:
                    - content: |
                            echo '<?php phpinfo();' >
                      path: /var/www/index.php
          listeners:
            - http:
                port: 80
                protocol: http
                algorithm: round_robin
            - https:
                port: 443
                protocol: http
                algorithm: round_robin

      - wordpress:
          domain: *domain
          ethernet: *bastion
          nodes:
            - wordpress_na12:
                description: '#wordpress #us #primary'
                cpu: 4 2 highperformance
                memory: 8
                glue:
                  - internet 22 80 443
                monitoring: essentials
                cloud-config:
                  disable_root: false
                  ssh_pwauth: True
                  packages:
                    - apache2
                    - php5
                    - php5-mysql
                    - mysql-server
                  runcmd:
                    - wget http://wordpress.org/latest.tar.gz -P /tmp/
                    - tar -zxf /tmp/latest.tar.gz -C /var/www/
                    - mysql -e "create database wordpress; create user 'wpuser'@'localhost' identified by 'changemetoo'; grant all privileges on wordpress . \* to 'wpuser'@'localhost'; flush privileges;"
                    - mysql -e "drop database test; drop user 'test'@'localhost'; flush privileges;"
                    - mysqladmin -u root password 'changeme'

      # workloads dealing with short-term memory
      - memcache:
          domain: *domain
          ethernet: *bastion
          nodes:
            - redis[1..2]_na12:
                description: '#redis #us #primary'
                memory: 32
                monitoring: essentials

      # docker resources
      - docker:
          domain: *domain
          ethernet: &compute
            name: gigafox.compute
            description: '#us'
            subnet: 10.3.0.0
            accept:
              - gigafox.control
              - gigafox.web
            destroy: never
          nodes:
            - docker[1..5]_na12:
                description: '#docker #us #primary'
                cpu: 32
                memory: 128
                monitoring: essentials
                rub:
                  - run rub.update.sh
                  - run rub.docker.sh

      # nodejs resources
      - nodejs:
          domain: *domain
          ethernet: *compute
          nodes:
            - nodejs[1..5]_na12:
                description: '#nodejs #us #primary'
                monitoring: essentials
                rub:
                  - run rub.update.sh

      # workloads dedicated to data records
      - sql:
          domain: *domain
          ethernet: &data
            name: gigafox.data
            description: '#us'
            subnet: 10.4.0.0
            accept:
              - gigafox.control
              - gigafox.compute
            destroy: never
          nodes:
            - masterSQL_na12:
                description: '#mysql #us #primary'
                appliance: 'RedHat 6 64-bit 4 CPU'
                monitoring: advanced

      # workloads dedicated to big data
      - cassandra:
          domain: *domain
          ethernet: *data
          nodes:
            - cassandra[1..3]_na12:
                description: '#cassandra #us #primary'
                monitoring: essentials

      # workloads dedicated to BLOBs
      - mongodb:
          domain: *domain
          ethernet: *data
          nodes:
            - mongodb[1..7]_na12:
                description: '#mongodb #us #primary'
                monitoring: essentials

      # workloads devoted to object-based storage
      - s3:
          domain: *domain
          ethernet: *data
          nodes:
            - ceph[1..5]_na12:
                description: '#ceph #us #primary'
                monitoring: essentials

    ---
    # Ashburn - primary site in USA
    locationId: NA9
    regionId: dd-na

    blueprints:

      # workloads dealing directly with end-user devices
      - web:
          domain: &domain
            name: Gigafox
            description: '#us #secondary'
            service: advanced
            ipv4: 4
          ethernet: &bastion
            name: gigafox.web
            description: '#us'
            subnet: 10.2.0.0
            accept:
              - NA12::gigafox.control
            destroy: never
          nodes:
            - web[1..2]_na9:
                description: '#apache #us #secondary'
                cpu: 4
                memory: 8
                disks:
                  - 1 500 standard
                monitoring: essentials
                rub:
                  - put rub.puppet.apache.pp /root/apache.pp
                  - run rub.puppet.apache.sh /root/apache.pp
          listeners:
            - http:
                port: 80
                protocol: http
                algorithm: round_robin
            - https:
                port: 443
                protocol: http
                algorithm: round_robin

      # workloads dealing with short-term memory
      - memcache:
          domain: *domain
          ethernet: *bastion
          nodes:
            - redis[1..2]_na9:
                description: '#redis #us #secondary'
                monitoring: essentials

      # docker resources
      - docker:
          domain: *domain
          ethernet: &compute
            name: gigafox.compute
            description: '#us'
            subnet: 10.3.0.0
            accept:
              - NA12::gigafox.control
            destroy: never
          nodes:
            - docker[1..5]_na9:
                description: '#docker #us #secondary'
                monitoring: essentials
                rub:
                  - run rub.update.sh
                  - run rub.docker.sh

      # nodejs resources
      - nodejs:
          domain: *domain
          ethernet: *compute
          nodes:
            - nodejs[1..5]_na9:
                description: '#nodejs #us #secondary'
                monitoring: essentials
                rub:
                  - run rub.update.sh

      # workloads dedicated to data records
      - sql:
          domain: *domain
          ethernet: &data
            name: gigafox.data
            description: '#us'
            subnet: 10.4.0.0
            accept:
              - NA12::gigafox.control
            destroy: never
          nodes:
            - slaveSQL_na9:
                description: '#mysql #us #secondary'
                appliance: 'RedHat 6 64-bit 4 CPU'
                monitoring: advanced

      # workloads dedicated to big data
      - cassandra:
          domain: *domain
          ethernet: *data
          nodes:
            - cassandra[1..3]_na9:
                description: '#cassandra #us #secondary'
                monitoring: essentials

      # workloads dedicated to BLOBs
      - mongodb:
          domain: *domain
          ethernet: *data
          nodes:
            - mongodb[1..7]_na9:
                description: '#mongodb #us #secondary'
                monitoring: essentials

      # workloads devoted to object-based storage
      - s3:
          domain: *domain
          ethernet: *data
          nodes:
            - ceph[1..5]_na9:
                description: '#ceph #us #secondary'
                monitoring: essentials

Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml build
    $ python -m plumbery fittings.yaml start
    $ python -m plumbery fittings.yaml prepare

These commands will build fittings as per the provided plan, and start
the server as well. Look at messages displayed by plumbery while it is
working, so you can monitor what's happening.

Destruction commands
--------------------

Cloud computing has a hard rule. Any resource has a cost, be it used or not.
At the end of every session, you are encouraged to destroy everything.
Hopefully, plumbery is making this really simple:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy

