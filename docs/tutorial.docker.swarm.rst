=====================================
Docker Swarm with multiple containers
=====================================

This is a cluster of coordinated Docker Engine nodes. This is behaving like
a swarm, with one queen (the manager) and seven bees (the workers). The demonstration
also covers the installation of Consul as a dynamic registry across nodes.

Requirements for this use case
------------------------------

* Add a Network Domain
* Add an Ethernet network
* Deploy a Ubuntu server as a manager -- the queen
* Deploy multiple large Ubuntu servers as Docker containers -- the bees
* Monitor all servers
* Assign a public IPv4 address to each server
* Add address translation rules to ensure Internet connectivity with each server
* Add firewall rules to accept TCP traffic on port 22 (ssh)
* Install Docker Engine at all servers
* Install Consul on the manager node to implement dynamic discovery back-end
* Run Docker Swarm Manager at the queen
* Run Docker Swarm at every other bee

Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. code-block:: yaml
   :linenos:

    ---

    defaults:

      cloud-config: # default for all nodes created by plumbery

        ssh_keys: # generated randomly, and used on subsequent invocations
          rsa_private: |
            {{ key.rsa_private }}
          rsa_public: "{{ key.rsa_public }}"

        users:
          - default

          - name: ubuntu
            sudo: 'ALL=(ALL) NOPASSWD:ALL'
            ssh-authorized-keys:
              - "{{ key.rsa_public }}"
              - "{{ local.rsa_public }}"

          - name: root
            ssh-authorized-keys:
              - "{{ key.rsa_public }}"
              - "{{ local.rsa_public }}"

        disable_root: false

        ssh_pwauth: false

    ---
    locationId: AU10
    regionId: dd-au

    blueprints:

      - swarm: queen bees

      - queen: # the master node for the full swarm

          domain: &domain
            name: DockerSwarmFox
            description: "Demonstration of a Docker swarm"
            ipv4: auto

          ethernet: &ethernet
            name: dockerSwarmNetwork
            subnet: 10.0.0.0

          nodes:
            - queen:

                description: "#docker #swarm #queen #ubuntu"

                information:
                  - "a Docker engine acting as the queen for the full swarm"
                  - "connect remotely with:"
                  - "$ ssh ubuntu@{{ queen.public }}"
                  - "check status of local docker with:"
                  - "$ docker info"
                  - "check swarm status with:"
                  - "$ docker -H :4000 info"
                  - "run redis in a container somewhere with:"
                  - "$ docker -H :4000 run --name some-redis -d redis"
                  - "check which node is running redis with:"
                  - "$ docker -H :4000 ps -l | grep redis"

                appliance: 'Ubuntu 14'

                cpu: 8
                memory: 32

                glue:
                  - internet 22

                monitoring: essentials

                cloud-config:

                  hostname: "{{ node.name }}"

                  packages:
                    - ntp

                  write_files:

                    - path: /root/hosts.awk
                      content: |
                        #!/usr/bin/awk -f
                        /^{{ queen.private }}/ {next}
                        /^{{ bee1.private }}/ {next}
                        /^{{ bee2.private }}/ {next}
                        /^{{ bee3.private }}/ {next}
                        /^{{ bee4.private }}/ {next}
                        /^{{ bee5.private }}/ {next}
                        /^{{ bee6.private }}/ {next}
                        /^{{ bee7.private }}/ {next}
                        {print}
                        END {
                         print "{{ queen.private }}    queen"
                         print "{{ bee1.private }}    bee1"
                         print "{{ bee2.private }}    bee2"
                         print "{{ bee3.private }}    bee3"
                         print "{{ bee4.private }}    bee4"
                         print "{{ bee5.private }}    bee5"
                         print "{{ bee6.private }}    bee6"
                         print "{{ bee7.private }}    bee7"
                        }

                    - path: /root/docker.sed
                      content: |
                        #!/usr/bin/sed
                        s/#DOCKER_OPTS/DOCKER_OPTS/
                        s|\-\-dns 8.8.8.8 \-\-dns 8.8.4.4|-H tcp://{{ node.private }}:2375 -H unix:///var/run/docker.sock|

                  runcmd:

                    - echo "===== Handling ubuntu identity"
                    - cp -n /etc/ssh/ssh_host_rsa_key /home/ubuntu/.ssh/id_rsa
                    - cp -n /etc/ssh/ssh_host_rsa_key.pub /home/ubuntu/.ssh/id_rsa.pub
                    - chown ubuntu:ubuntu /home/ubuntu/.ssh/*
                    - sed -i "/StrictHostKeyChecking/s/^.*$/    StrictHostKeyChecking no/" /etc/ssh/ssh_config

                    - echo "===== Updating /etc/hosts"
                    - cp -n /etc/hosts /etc/hosts.original
                    - awk -f /root/hosts.awk /etc/hosts >/etc/hosts.new && mv /etc/hosts.new /etc/hosts

                    - echo "===== Installing docker"
                    - curl -sSL https://get.docker.com/ | sh
                    - sed -i -f /root/docker.sed /etc/default/docker
                    - restart docker
                    - usermod -aG docker ubuntu
                    - su ubuntu -c "docker run hello-world"

                    - echo "===== Running consul"
                    - docker run -d -p 8500:8500 --name=consul --restart=always -h {{ node.name }} progrium/consul -server -bootstrap -advertise {{ node.private }}

                    - echo "===== Running swarm manager"
                    - docker run -d -p 4000:4000 --name=swarmMgr --restart=always swarm manage -H :4000 --advertise {{ node.private }}:4000  consul://{{ node.private }}:8500
                    - docker ps

      - bees: # some bees contributing to the swarm

          domain: *domain
          ethernet: *ethernet
          nodes:
            - bee[1..7]:

                description: "#docker #swarm #bee #ubuntu"

                information:
                  - "a Docker engine acting as a worker bee for the full swarm"

                appliance: 'Ubuntu 14'

                cpu: 8
                memory: 32

                glue:
                  - internet 22

                monitoring: essentials

                cloud-config:

                  hostname: "{{ node.name }}"

                  packages:
                    - ntp

                  write_files:

                    - path: /root/hosts.awk
                      content: |
                        #!/usr/bin/awk -f
                        /^{{ queen.private }}/ {next}
                        /^{{ bee1.private }}/ {next}
                        /^{{ bee2.private }}/ {next}
                        /^{{ bee3.private }}/ {next}
                        /^{{ bee4.private }}/ {next}
                        /^{{ bee5.private }}/ {next}
                        /^{{ bee6.private }}/ {next}
                        /^{{ bee7.private }}/ {next}
                        {print}
                        END {
                         print "{{ queen.private }}    queen"
                         print "{{ bee1.private }}    bee1"
                         print "{{ bee2.private }}    bee2"
                         print "{{ bee3.private }}    bee3"
                         print "{{ bee4.private }}    bee4"
                         print "{{ bee5.private }}    bee5"
                         print "{{ bee6.private }}    bee6"
                         print "{{ bee7.private }}    bee7"
                        }

                    - path: /root/docker.sed
                      content: |
                        #!/usr/bin/sed
                        s/#DOCKER_OPTS/DOCKER_OPTS/
                        s|\-\-dns 8.8.8.8 \-\-dns 8.8.4.4|-H tcp://{{ node.private }}:2375 -H unix:///var/run/docker.sock|

                  runcmd:

                    - echo "===== Handling ubuntu identity"
                    - cp -n /etc/ssh/ssh_host_rsa_key /home/ubuntu/.ssh/id_rsa
                    - cp -n /etc/ssh/ssh_host_rsa_key.pub /home/ubuntu/.ssh/id_rsa.pub
                    - chown ubuntu:ubuntu /home/ubuntu/.ssh/*
                    - sed -i "/StrictHostKeyChecking/s/^.*$/    StrictHostKeyChecking no/" /etc/ssh/ssh_config

                    - echo "===== Updating /etc/hosts"
                    - cp -n /etc/hosts /etc/hosts.original
                    - awk -f /root/hosts.awk /etc/hosts >/etc/hosts.new && mv /etc/hosts.new /etc/hosts

                    - echo "===== Installing docker"
                    - curl -sSL https://get.docker.com/ | sh
                    - sed -i -f /root/docker.sed /etc/default/docker
                    - restart docker
                    - usermod -aG docker ubuntu
                    - su ubuntu -c "docker -H {{ node.name }}:2375 run hello-world"

                    - echo "===== Running swarm"
                    - sleep 1m
                    - docker run -d --name=swarm --restart=always swarm join --advertise={{ node.private }}:2375 consul://{{ queen.private }}:8500
                    - docker ps


Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

These commands will build fittings as per the provided plan, start all servers
and bootstrap them.

You can find the public address assigned to the manager server like this:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml ping


Follow-up commands
------------------

In this use case you can use the IPv4 assigned to the manager for direct ssh
connection.

.. sourcecode:: bash

    $ ssh ubuntu@<ipv4_here>

From there you will check both the status of the local Docker Engine, and the
status from the full Docker Swarm:

.. sourcecode:: bash

    $ docker info
    $ docker -H :4000 info

Next step is to run a new Redis container somewhere in the swarm:

.. sourcecode:: bash

    $ docker -H :4000 run --name some-redis -d redis

And, of course, you may want to identify which node is running redis
exactly:

.. sourcecode:: bash

    $ docker -H :4000 ps -l | grep redis

Destruction commands
--------------------

The more servers you have, the more costly it is. Would you like to stop the
invoice?

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml dispose

