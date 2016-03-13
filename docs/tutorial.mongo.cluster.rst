========================
Cluster of MongoDB nodes
========================

MongoDB is a database that is really well-adapted to real-time data analytics.
In this tutorial we will deploy multiple servers, and glue them together.

Requirements for this use case
------------------------------

* Add a Network Domain
* Add an Ethernet network
* Deploy multiple servers servers
* Monitor these servers
* Add mongoDB to the servers
* Create a cluster of configuration servers
* Add sharding servers


Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. code-block:: yaml
   :linenos:

    ---
    locationId: EU8 # London in Europe
    regionId: dd-eu

    blueprints:

      - mongo: mongo_config mongo_mongos mongo_shard

      - mongo_config:

          domain: &domain
            name: MongoFox
            service: essentials
            ipv4: 12

          ethernet: &ethernet
            name: mongofox.servers
            subnet: 192.168.20.0

          nodes:

            - mongo_config0[1..3]:

                glue:
                  - internet 22

                cloud-config:
                  disable_root: false
                  ssh_pwauth: True
                  packages:
                    - ntp

                  write_files: # replica set for configuration servers

                    - path: /etc/mongod.conf.sed
                      content: |
                         s/#sharding:/sharding:\n   clusterRole: configsvr\nreplication:\n  replSetName: configReplSet/

                  runcmd:
                    - "sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927"
                    - echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list
                    - sudo apt-get update
                    - sudo apt-get install -y mongodb-org
                    - cp -n /etc/mongod.conf /etc/mongod.conf.original
                    - sed -i -f /etc/mongod.conf.sed /etc/mongod.conf
                    - sudo service mongod restart

      - mongo_mongos:

          domain: *domain
          ethernet: *ethernet

          nodes:

            - mongo_mongos01:

                glue:
                  - internet 22

                cloud-config:
                  disable_root: false
                  ssh_pwauth: True
                  packages:
                    - ntp

                  write_files: # replica set for mongos servers

                    - path: /etc/mongod.conf.sed
                      content: |
                         s/#sharding:/sharding:\n   configDB: "configReplSet/{{mongo_config01}}:27019,{{mongo_config02}}:27019,{{mongo_config03}}:27019"/

                  runcmd:
                    - "sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927"
                    - echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list
                    - sudo apt-get update
                    - sudo apt-get install -y mongodb-org
                    - cp -n /etc/mongod.conf /etc/mongod.conf.original
                    - sed -i -f /etc/mongod.conf.sed /etc/mongod.conf
                    - sudo service mongod restart

      - mongo_shard:

          domain: *domain
          ethernet: *ethernet

          nodes:

            - mongo_shard0[1..2]:

                glue:
                  - internet 22

                cloud-config:
                  disable_root: false
                  ssh_pwauth: True
                  packages:
                    - ntp

                  write_files: # replica set for sharding servers

                    - path: /etc/mongod.conf.sed
                      content: |
                         s/#sharding:/sharding:\n   clusterRole: shardsvr/

                  runcmd:
                    - "sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927"
                    - echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list
                    - sudo apt-get update
                    - sudo apt-get install -y mongodb-org
                    - cp -n /etc/mongod.conf /etc/mongod.conf.original
                    - sed -i -f /etc/mongod.conf.sed /etc/mongod.conf
                    - sudo service mongod restart

Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

These commands build fittings as per the provided plan, start servers
and bootstrap them. The last command will display the name and password
used to configure the database.

You can check status of servers like this:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml ping

Follow-up commands
------------------

TO BE COMPLETED

Destruction commands
--------------------

The more servers you have, the more costly it is. Would you like to stop the
invoice?

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy

