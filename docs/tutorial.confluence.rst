================================
Confluence server from Atlassian
================================

This is a simple Confluence server for your team of developers.

Requirements for this use case
------------------------------

* Add a Network Domain
* Add an Ethernet network
* Deploy a Ubuntu server
* Add server to real-time dashboard
* Assign a public IPv4 address to the server
* Add address translation to ensure end-to-end IP connectivity
* Add firewall rule to accept TCP traffic on port 22 (ssh) and web (8090)
* Install Confluence in unattended mode

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
    locationId: EU8
    regionId: dd-eu

    blueprints:

      - confluence:

          domain:
            name: ConfluenceFox
            description: "Demonstration of a standalone Confluence server"
            service: essentials
            ipv4: 2

          ethernet:
            name: confluencefox.servers
            subnet: 192.168.20.0

          nodes:

            - confluence01:
                cpu: 2
                memory: 4
                monitoring: essentials
                glue:
                  - internet 22 8090

                description: "#confluence #atlassian #ubuntu"

                information:
                  - "this is a Confluence server for a small team"
                  - "connect remotely with a browser at following address:"
                  - "http://{{ node.public }}:8090/"

                appliance: 'Ubuntu 14'

                cloud-config:

                  packages:
                    - ntp

                  write_files:

                    - path: /root/response.varfile
                      content: |
                        #install4j response file for Confluence 5.9.4
                        #Tue Feb 09 17:27:13 EST 2016
                        executeLauncherAction$Boolean=true
                        app.install.service$Boolean=true
                        sys.confirmedUpdateInstallationString=false
                        existingInstallationDir=/usr/local/Confluence
                        sys.languageId=en
                        sys.installationDir=/opt/atlassian/confluence

                  runcmd:

                    - echo "===== Handling ubuntu identity"
                    - cp -n /etc/ssh/ssh_host_rsa_key /home/ubuntu/.ssh/id_rsa
                    - cp -n /etc/ssh/ssh_host_rsa_key.pub /home/ubuntu/.ssh/id_rsa.pub
                    - chown ubuntu:ubuntu /home/ubuntu/.ssh/*
                    - sed -i "/StrictHostKeyChecking/s/^.*$/    StrictHostKeyChecking no/" /etc/ssh/ssh_config

                    - echo "===== Installing Confluence"
                    - cd /root
                    - wget -nv https://www.atlassian.com/software/confluence/downloads/binary/atlassian-confluence-5.9.4-x64.bin
                    - chmod a+x atlassian-confluence-5.9.4-x64.bin
                    - ./atlassian-confluence-5.9.4-x64.bin -q -varfile /root/response.varfile


Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

These commands will build fittings as per the provided plan, start the server
and bootstrap it.

You can find the public address assigned to the server like this:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml ping


Follow-up commands
------------------

In this use case you can use the IPv4 assigned to the manager for direct web
browsing, but on unusual port number::

    http://<ipv4_here>:8090/


This command is self-explanatory and validates the system installation.

Destruction commands
--------------------

The more servers you have, the more costly it is. Would you like to stop the
invoice?

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml dispose

