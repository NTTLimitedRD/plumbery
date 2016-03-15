============================================================
Centralised logging with Elasticsearch, Logstash, and Kibana
============================================================

In this tutorial, we will go over the installation of Elasticsearch, Logstash,
and Kibana, the so-called ELK stack. Logstash is an open source tool for
collecting, parsing, and storing logs for future use. Kibana is a web interface
that can be used to search and view the logs that Logstash has indexed. Both
Logstash and Kibana rely on Elasticsearch for powerful storage and retrieval
of information. The ELK combination provides an effective service that allow
system administrators to consolidate logs from various parts of their information
systems, and to dig into global logs visually when required.

Centralized logging can be very useful when attempting to identify problems with
your servers or applications, as it allows you to search through all of your
logs in a single place. It is also useful because it allows you to identify
issues that span multiple servers by correlating their logs during a specific time frame.

It is possible to use Logstash to gather logs of all types, but we will limit
the scope of this tutorial to syslog gathering. We will demonstrate in this
tutorial how a remote server can be equipped to export logs automatically and
securely to the ELK facility. In the fittings plan below, this is named `logstash client`.


Requirements for this use case
------------------------------

* Add multiple Network Domains and Ethernet networks to support the distribution of nodes at several data centres
* Deploy one Linux server for the ELK node, and one for each remote node
* Add a virtual disk of 500 GB to the ELK node
* Monitor all nodes in the real-time dashboard provided by Dimension Data
* Assign public IPv4 addresses for ssh access over the Internet
* Add address translation to ensure end-to-end IP connectivity
* Add firewall rule to accept TCP traffic on port 22 (ssh)
* Add firewall rule to allow web traffic to Kibana
* Allow IPv6 traffic between remote nodes and the ELK node
* Expand file system of the ELK node with added disk (LVM)
* Install a new SSH key to secure remote communications across all nodes
* Update `etc/hosts` to bind IPv6 addresses to host names
* Manage keys to suppress passwords in SSH connections
* Install Elasticsearch, Logstash and Kibana to the ELK node
* Install Logstash to every other node
* Create a private key and self-signed certificate at the ELK node to secure Logstash operations over IPv6
* Install the certificate at every other node to secure communications from Logstash client software

Fittings plan
-------------

The plan below demonstrates multiple interesting tips and tricks:

* Provide SSH access to all nodes via public IPv4, NAT, and firewall settings
* Management of SSH keys to enable secured communications without passwords
* Allow private IPv6 communications between remote nodes and the ELK node
* Automatic registration of all nodes to the monitoring services provided by Dimension Data
* Update of `etc/hosts` with IPv6
* Remove Apache, and install Nginx instead
* Install the full ELK stack
* Configure Nginx as efficient and secured proxy to Kibana
* Orchestrate generation and configuration of web password to the Kibana dashboard
* Automate the installation of Oracle 8 JDK
* User documentation of the infrastructure is put directly in the fittings plan

`Download this fittings plan`_ if you want to hack it for yourself. This is part of `the demonstration
directory of the plumbery project`_ at GitHub. Alternatively, you can copy the
text below and put it in a text file named ``fittings.yaml``.

.. code-block:: yaml
   :linenos:

    ---

    information:
      - "Centralised logging with Elasticsearch, Logstash, and Kibana."

    links:
      documentation: https://plumbery.readthedocs.org/en/latest/tutorial.elk.html
      credit: http://www.exonet3i.net/evernote/How%20To%20Install%20Elasticsearch,%20Logstash,%20and%20K%20%5B3%5D.html

    defaults:

      # the same network domain is used at various facilities
      #
      domain:
        name: ELKFox
        description: "Demonstration of Elasticsearch, Logstash and Kibana"
        ipv4: auto

      # the same ethernet configuration is used at various facilities
      #
      ethernet:
        name: ELKNetwork
        subnet: 10.0.0.0

      # default settings for a remote logger
      #
      logstashForwarder:

        description: "#logstash-forwarder #ubuntu"

        information:
          - "a remote server with logstash-forwarder"

        appliance: 'Ubuntu 14'

        cpu: 2
        memory: 4

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
                /^{{ node.private }}/ {next}
                /^{{ node.ipv6 }}/ {next}
                /^{{ dd-au::AU10::logstashServer.ipv6 }}/ {next}
                {print}
                END {
                 print "{{ node.private }}    {{ node.name }}"
                 print "{{ node.ipv6 }}    {{ node.name }}"
                 print "{{ dd-au::AU10::logstashServer.ipv6 }}    logstashServer"
                }

            - path: /root/logstash-forwarder.conf
              content: |
                {
                  "network": {
                    "servers": [ "{{ dd-au::AU10::logstashServer.ipv6 }}:5000" ],
                    "timeout": 15,
                    "ssl ca": "/etc/logstash-pki/logstash-forwarder.crt"
                  },

                  "files": [
                    {
                      "paths": [
                        "/var/log/syslog",
                        "/var/log/auth.log"
                       ],
                      "fields": { "type": "syslog" }
                    }
                  ]
                }

          runcmd:

            - echo "===== Handling ubuntu identity"
            - cp -n /etc/ssh/ssh_host_rsa_key /home/ubuntu/.ssh/id_rsa
            - cp -n /etc/ssh/ssh_host_rsa_key.pub /home/ubuntu/.ssh/id_rsa.pub
            - chown ubuntu:ubuntu /home/ubuntu/.ssh/*
            - sed -i "/StrictHostKeyChecking/s/^.*$/    StrictHostKeyChecking no/" /etc/ssh/ssh_config

            - echo "===== Updating /etc/hosts"
            - cp -n /etc/hosts /etc/hosts.original
            - awk -f /root/hosts.awk /etc/hosts >/etc/hosts.new && mv /etc/hosts.new /etc/hosts

            - echo "===== Installing logstash-forwarder"
            - cd /root
            - wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
            - echo "deb http://packages.elastic.co/logstashforwarder/debian stable main" | sudo tee /etc/apt/sources.list.d/logstashforwarder.list
            - apt-get update
            - apt-get install logstash-forwarder

            - echo "===== Securing logstash-forwarder"
            - sleep 1m
            - mkdir /etc/logstash-pki
            - rsync -zhave "ssh -i /home/ubuntu/.ssh/id_rsa" ubuntu@logstashServer:/var/rsync/logstash-forwarder.crt /etc/logstash-pki

            - echo "===== Configuring logstash"
            - cp -n /etc/logstash-forwarder.conf /etc/logstash-forwarder.conf.origin
            - cp /root/logstash-forwarder.conf /etc/logstash-forwarder.conf
            - service logstash-forwarder restart


      # default settings for all nodes created by plumbery
      #
      cloud-config:

        # plumbery generates a random key pair
        #
        ssh_keys:
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

      - logstash:

          ethernet:
            accept:
              - dd-ap::AP5::ELKNetwork

          nodes:

            - logstashServer:  # a combo of logstash, elasticsearch, and kibana

                description: "#logstash #elasticsearch #dashboard #kibana #ubuntu"

                information:
                  - "a web dashboard to visualize logs:"
                  - "http://{{ node.public }}"
                  - "authenticate with 'dashboard' and '{{ dashboard.secret }}'"
                  - "troubleshoot with:"
                  - "$ ssh ubuntu@{{ node.public }}"
                  - "check the feeding of elasticsearch with:"
                  - "$ curl 'http://localhost:9200/_cat/indices?v'"
                  - "validate the configuration of logstash with:"
                  - "$ service logstash configtest"

                appliance: 'Ubuntu 14'

                cpu: 2
                memory: 4

                disks:
                  - 1 500 standard

                glue:
                  - internet 22 80

                monitoring: essentials

                cloud-config:

                  hostname: "{{ node.name }}"

                  bootcmd:

                    # remove apache
                    - apt-get remove apache2 -y
                    - apt-get autoremove -y

                    # automate acceptance of oracle licence
                    - echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | sudo debconf-set-selections
                    - echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 seen true" | sudo debconf-set-selections

                  apt_sources:
                    - source: "ppa:webupd8team/java"

                  packages:
                    - ntp
                    - oracle-java8-installer
                    - nginx
                    - apache2-utils
                    - python-pip

                  write_files:

                    - path: /root/hosts.awk
                      content: |
                        #!/usr/bin/awk -f
                        /^{{ node.private }}/ {next}
                        /^{{ node.ipv6 }}/ {next}
                        /^{{ logstash-AU10.ipv6 }}/ {next}
                        /^{{ dd-ap::AP5::logstash-AP5.ipv6 }}/ {next}
                        {print}
                        END {
                         print "{{ node.private }}    {{ node.name }}"
                         print "{{ node.ipv6 }}    {{ node.name }}"
                         print "{{ logstash-AU10.ipv6 }}    logstash-AU10"
                         print "{{ dd-ap::AP5::logstash-AP5.ipv6 }}    logstash-AP5"
                        }

                    - path: /root/nginx-sites-available-default
                      content: |
                        server {
                            listen 80;

                            server_name {{ node.public }};

                            auth_basic "Restricted Access";
                            auth_basic_user_file /etc/nginx/htpasswd.users;

                            location / {
                                proxy_pass http://localhost:5601;
                                proxy_http_version 1.1;
                                proxy_set_header Upgrade $http_upgrade;
                                proxy_set_header Connection 'upgrade';
                                proxy_set_header Host $host;
                                proxy_cache_bypass $http_upgrade;
                            }
                        }

                    - path: /root/logstash-conf.d-01-lumberjack-input.conf
                      content: |
                        input {
                          lumberjack {
                            port => 5000
                            type => "logs"
                            ssl_certificate => "/etc/pki/tls/certs/logstash-forwarder.crt"
                            ssl_key => "/etc/pki/tls/private/logstash-forwarder.key"
                          }
                        }

                    - path: /root/logstash-conf.d-10-syslog.conf
                      content: |
                        filter {
                          if [type] == "syslog" {
                            grok {
                              match => { "message" => "%{SYSLOGTIMESTAMP:syslog_timestamp} %{SYSLOGHOST:syslog_hostname} %{DATA:syslog_program}(?:\[%{POSINT:syslog_pid}\])?: %{GREEDYDATA:syslog_message}" }
                              add_field => [ "received_at", "%{@timestamp}" ]
                              add_field => [ "received_from", "%{host}" ]
                            }
                            syslog_pri { }
                            date {
                              match => [ "syslog_timestamp", "MMM  d HH:mm:ss", "MMM dd HH:mm:ss" ]
                            }
                          }
                        }

                    - path: /root/logstash-conf.d-30-lumberjack-output.conf
                      content: |
                        output {
                          elasticsearch { hosts => localhost }
                          stdout { codec => rubydebug }
                        }

                    - path: /root/etc-cron.d-elasticsearch_curator
                      content: |
                        @midnight     root        curator delete --older-than 120 >> /var/log/curator.log 2>&1

                  runcmd:

                    - echo "===== Growing LVM with added disk"
                    - pvcreate /dev/sdb
                    - vgextend rootvol00 /dev/sdb
                    - lvextend -l +100%FREE /dev/mapper/rootvol00-rootlvol00
                    - resize2fs /dev/mapper/rootvol00-rootlvol00

                    - echo "===== Handling ubuntu identity"
                    - cp -n /etc/ssh/ssh_host_rsa_key /home/ubuntu/.ssh/id_rsa
                    - cp -n /etc/ssh/ssh_host_rsa_key.pub /home/ubuntu/.ssh/id_rsa.pub
                    - chown ubuntu:ubuntu /home/ubuntu/.ssh/*
                    - sed -i "/StrictHostKeyChecking/s/^.*$/    StrictHostKeyChecking no/" /etc/ssh/ssh_config

                    - echo "===== Updating /etc/hosts"
                    - cp -n /etc/hosts /etc/hosts.original
                    - awk -f /root/hosts.awk /etc/hosts >/etc/hosts.new && mv /etc/hosts.new /etc/hosts

                    - echo "===== Installing logstash, elasticsearch, kibana"
                    - cd /root
                    - wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
                    - echo "deb http://packages.elastic.co/elasticsearch/2.x/debian stable main" | sudo tee -a /etc/apt/sources.list.d/elasticsearch-2.x.list
                    - echo "deb http://packages.elastic.co/kibana/4.4/debian stable main" | sudo tee -a /etc/apt/sources.list.d/kibana-4.4.x.list
                    - echo "deb http://packages.elastic.co/logstash/2.2/debian stable main" | sudo tee -a /etc/apt/sources.list.d/logstash-2.2.x.list
                    - apt-get update
                    - apt-get install logstash elasticsearch kibana
                    - update-rc.d elasticsearch defaults 95 10
                    - service elasticsearch start
                    - update-rc.d kibana defaults 96 9
                    - service kibana start

                    - echo "===== Securing logstash"
                    - cp -n /etc/ssl/openssl.cnf /etc/ssl/openssl.cnf.origin
                    - sed -i "/# subjectAltName=email:copy/s/^.*$/subjectAltName = IP:{{ node.ipv6 }}/" /etc/ssl/openssl.cnf
                    - mkdir /etc/logstash-pki
                    - cd /etc/logstash-pki
                    - openssl req -config /etc/ssl/openssl.cnf -x509 -days 3650 -batch -nodes -newkey rsa:2048 -keyout logstash-forwarder.key -out logstash-forwarder.crt
                    - openssl x509 -in logstash-forwarder.crt -text -noout

                    - echo "===== Sharing certificate for remote access"
                    - mkdir /var/rsync
                    - cp /etc/logstash-pki/logstash-forwarder.crt /var/rsync
                    - chown -R ubuntu:ubuntu /var/rsync

                    - echo "===== Configuring logstash"
                    - cp /root/logstash-conf.d-01-lumberjack-input.conf /etc/logstash/conf.d/01-lumberjack-input.conf
                    - cp /root/logstash-conf.d-10-syslog.conf /etc/logstash/conf.d/10-syslog.conf
                    - cp /root/logstash-conf.d-30-lumberjack-output.conf /etc/logstash/conf.d/30-lumberjack-output.conf
                    - service logstash restart

                    - echo "===== Securing web access to Kibana"
                    - cp -n /etc/nginx/sites-available/default /etc/nginx/sites-available/default.original
                    - cp /root/nginx-sites-available-default /etc/nginx/sites-available/default
                    - htpasswd -cb /etc/nginx/htpasswd.users dashboard {{ dashboard.secret }}
                    - service nginx restart

                    - echo "===== Installing Curator to purge old logs"
                    - pip install elasticsearch-curator
                    - cp /root/etc-cron.d-elasticsearch_curator /etc/cron.d/elasticsearch_curator


            - logstash-AU10:
                default: logstashForwarder

    ---
    locationId: AP5
    regionId: dd-ap

    blueprints:

      - bees:

          ethernet:
            accept:
              - dd-au::AU10::ELKNetwork

          nodes:
            - logstash-AP5:
                default: logstashForwarder

Deployment commands
-------------------

For this tutorial, plumbery has to connect separately to multiple data centres
and to apply several changes in multiple waves.

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

This command will build fittings as per the provided plan, and start
servers as well. Look at messages displayed by plumbery while it is
working, so you can monitor what's happening.

Follow-up commands
------------------

At the end of the deployment, plumbery will display on screen some instructions
to help you move forward. You can ask plumbery to display this information
at any time with the following command:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml information

What's coming next? You may want to connect to the ELK node in ssh and
check the stream of records coming from remote nodes via Logstash.

.. sourcecode:: bash

    $ ssh ubuntu@<IPv4 of ELK node>
    $ curl 'http://localhost:9200/_cat/indices?v'

Repeat the command multiple times and check the increment of documents indexed
by Elasticsearch.

If everything is looking fine at this stage, then you are allowed to move
to the configuration of the Kibana interactive dashboard. In a browser window,
type the public IPv4 address of the ELK node. When asked for it, provide
the name and the password that were mentioned by plumbery during the deployment
of the fittings plan.

From there you can configure the dashboard as per your
very specific needs.

Destruction commands
--------------------

Launch following command to remove all resources involved in the fittings plan:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml dispose


.. _`Download this fittings plan`: https://github.com/bernard357/plumbery/blob/master/demos/elk.yaml
.. _`the demonstration directory of the plumbery project`: https://github.com/bernard357/plumbery/tree/master/demos