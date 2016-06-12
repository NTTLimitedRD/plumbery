Fittings schema documentation
===============================

This is the list of keywords that are known by plumbery, and that can be used
in a fittings file. You will find some comprehensive example at the bottom of this page.

  =======================  ==========  ================================================================================================
  Keyword                   Required    Description
  =======================  ==========  ================================================================================================
  appliance                 yes         The name of the image to deploy, .e.g., 'Ubuntu'. See :doc:`fittings.appliance`
  backup                    no          Details of the cloud backup configuration. See :doc:`fittings.backup`
  blueprints                yes         A collection of blueprints
  cloud-config              no          The cloud-config details, see :doc:`fittings.cloud-config`
  cpu                       no          The number of CPU, or the CPU configuration. See :doc:`fittings.cpu`
  defaults                  no          A map of default values. See :doc:`fittings.default`
  description               no          A one-line description that can have hashtags, e.g., 'This is #ubuntu #master node'
  disks                     no          A list of the disk configurations, the ID size (Gb) and speed. See :doc:`fittings.disks`
  domain                    yes         A description of a network domain. See :doc:`fittings.domain`
  ethernet                  yes         A description of a VLAN. See :doc:`fittings.ethernet`
  glue                      no          Connect a node to the Internet or add NICs. See :doc:`fittings.glue`
  information               no          A list of strings explaining what the fittings does
  links                     no          A map, including 'documentation' and 'credit' as possible values
  listeners                 no          A collection of listener objects, describing load balancers settings
  locationId                yes         The id of a target data centre, e.g., 'EU6'; See :doc:`locationId`
  memory                    no          The amount of RAM in gigabytes
  monitoring                no          The monitoring plan to configure, either **essentials** or **advanced**. No default
  nodes                     yes         A collection of node objects, describing the servers to be deployed
  parameters                no          Settings that can be provided externally to plumbery
  running                   no          If set to **always**, then plumbery cannot delete the fittings
  =======================  ==========  ================================================================================================

Complete example::

.. sourcecode:: yaml

    ---

    information:
      - "Let's Chat server, self-hosted chat for private teams"

    parameters:

      locationId:
        information:
          - "the target data centre for this deployment"
        type: locations.list
        default: EU6

    links:
      documentation: https://github.com/DimensionDataCBUSydney/plumbery-contrib/tree/master/fittings/collaboration/letschat
      credit: https://mborgerson.com/setting-up-lets-chat-on-ubuntu

    defaults:

      cloud-config:

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

        disable_root: true
        ssh_pwauth: false

    ---

    locationId: "{{ parameter.locationId }}"

    blueprints:

      - letschat:

          domain:
            name: myDomain
            ipv4: 2

          ethernet:
            name: myNetwork
            subnet: 10.0.0.0

          nodes:
            - letschat01:

                description: "#chat server #ubuntu"

                information:
                  - "this is the Let's Chat server for our team"
                  - "browse http://{{ node.public }}:5000/ to enter conversations"

                appliance: 'Ubuntu 14'
                cpu: 8
                memory: 32

                disks:
                  - 1 50 standard

                glue:
                  - internet 22 5000

                monitoring: essentials

                cloud-config:
                  hostname: "{{ node.name }}"

                  packages:
                    - nodejs
                    - npm
                    - nodejs-legacy
                    - mongodb
                    - mongodb-server
                    - git

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

                    - echo "===== Installing Let's Chat"
                    - cd /home/ubuntu
                    - git clone https://github.com/sdelements/lets-chat.git
                    - cd lets-chat
                    - npm install
                    - cp settings.yml.sample settings.yml
                    - sed -i "/host:/s/'[^']*'/'{{ node.name }}'/" settings.yml

                    - echo "===== Starting the server"
                    - npm start
