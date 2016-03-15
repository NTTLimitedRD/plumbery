========================
Cluster of Redis servers
========================

Redis is a key-value database that is providing superior performance to
web site and to application servers. In this tutorial we will orchestrate
a cluster of multiple servers.

Requirements for this use case
------------------------------

* Add a Network Domain
* Add an Ethernet network
* Deploy multiple servers servers
* Monitor these servers
* Add redis to the servers
* Configure one server as the master
* Configure other servers to replicate the master


Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. code-block:: yaml
   :linenos:

    ---
    locationId: NA12
    regionId: dd-na

    blueprints:

      - redis:

          domain:
            name: RedisFox
            service: essentials
            ipv4: 4

          ethernet:
            name: redisfox.servers
            subnet: 192.168.20.0

          nodes:

            - redis01: # master server

                cpu: 2
                memory: 4
                monitoring: essentials
                glue:
                  - internet 22

                information:
                  - "after the setup, connect via ssh to {{ node.public }} to check the status of the cluster"
                  - "then use following commands:"
                  - "redis-cli -h 127.0.0.1 -p 6379"
                  - "> AUTH {{ master.secret }}"
                  - "OK"
                  - "> INFO"
                  - " ... "
                  - "# Replication"
                  - "role:master"
                  - "connected_slaves:3"

                cloud-config:
                  disable_root: false
                  ssh_pwauth: true
                  apt_sources:
                    - source: "ppa:chris-lea/redis-server"
                  packages:
                    - ntp
                    - redis-server
                  write_files:
                    - path: /root/edit_redis_conf.sed
                      content: |
                        #!/usr/bin/sed
                        s/tcp-keepalive 0/tcp-keepalive 60/
                        /^bind 127.0.0.1/s/^/#/
                        s/# requirepass foobared/requirepass {{ master.secret }}/
                        s/# maxmemory-policy volatile-lru/maxmemory-policy noeviction/
                  runcmd:
                    - cp -n /etc/redis/redis.conf /etc/redis/redis.conf.original
                    - sed -i -f /root/edit_redis_conf.sed /etc/redis/redis.conf
                    - sudo service redis-server restart

            - redis0[2..4]: # slave servers

                cpu: 2
                memory: 4
                monitoring: essentials
                glue:
                  - internet 22

                information:
                  - "this slave server connects automatically to the master server"

                cloud-config:
                  disable_root: false
                  ssh_pwauth: true
                  apt_sources:
                    - source: "ppa:chris-lea/redis-server"
                  packages:
                    - ntp
                    - redis-server
                  write_files:
                    - content: |
                        #!/usr/bin/sed
                        s/tcp-keepalive 0/tcp-keepalive 60/
                        /^bind 127.0.0.1/s/^/#/
                        s/# requirepass foobared/requirepass {{ random.secret }}/
                        s/# maxmemory-policy volatile-lru/maxmemory-policy noeviction/
                        s/# slaveof <masterip> <masterport>/slaveof {{ redis01.private }} 6379/
                        s/# masterauth <master-password>/masterauth {{ master.secret }}/

                      path: /root/edit_redis_conf.sed
                  runcmd:
                    - cp -n /etc/redis/redis.conf /etc/redis/redis.conf.original
                    - sed -i -f /root/edit_redis_conf.sed /etc/redis/redis.conf
                    - sudo service redis-server restart


Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

These commands build fittings as per the provided plan, start servers
and bootstrap them. The last command will display the secret used to
authenticate to the redis master server.

You can check status of servers like this:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml ping

Follow-up commands
------------------

After the setup, connect via ssh to redis01 to check the status of the cluster::

    $ ssh root@<ipv4_of_redis01>
    $ redis-cli -h 127.0.0.1 -p 6379
    > AUTH {{ random.secret }}
    OK
    > INFO
    ...
    # Replication
    role:master
    connected_slaves:3

Destruction commands
--------------------

The more servers you have, the more costly it is. Would you like to stop the
invoice?

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy

