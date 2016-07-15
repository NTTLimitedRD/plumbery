The structure and content of fittings file
==========================================

Keywords used by plumbery
-------------------------

This is the list of keywords that are known by plumbery, and that can be used
in a fittings file. You will find some comprehensive example at the bottom of this page.

==============  ========  ==========================================================================================
Keyword         Required  Description
==============  ========  ==========================================================================================
apiHost         yes       A private API endpoint. See :doc:`fittings.facility`
appliance       yes       Name of the image to deploy, .e.g., 'Ubuntu'. See :doc:`fittings.appliance`
backup          no        Cloud backup configuration. See :doc:`fittings.backup`
beachhead       no        Advanced networking setting. See :doc:`fittings.beachhead`
blueprints      yes       A collection of blueprints
cloud-config    no        The cloud-config details. See :doc:`fittings.cloud-config`
cpu             no        The number of CPU, or the CPU configuration. See :doc:`fittings.compute`
default         no        The class of some fittings. See :doc:`fittings.defaults`
defaults        no        A map of default values. See :doc:`fittings.defaults`
description     no        One line of text with hashtags, e.g., 'This is #ubuntu #master node'
disks           no        Storage type and size. See :doc:`fittings.disks`
domain          yes       See :doc:`fittings.domain`
ethernet        yes       See :doc:`fittings.ethernet`
glue            no        See :doc:`fittings.glue`
information     no        A list of strings explaining what the fittings does
links           no        A map, including 'documentation' and 'credit' as possible values
listeners       no        A collection of listener objects, describing load balancers settings
locationId      yes       Target data centre, e.g., 'EU6'. See :doc:`fittings.facility`
memory          no        Amount of RAM in gigabytes. See :doc:`fittings.compute`
monitoring      no        Monitoring plan, either **essentials** or **advanced**. No default
nodes           yes       A collection of node objects, describing the servers to be deployed
parameters      no        Settings that can be provided externally to plumbery
regionId        no        Identify API endpoint, e.g., 'dd-ap'. See :doc:`fittings.facility`
running         no        If set to **always**, then plumbery cannot delete the fittings
==============  ========  ==========================================================================================

Multiple documents in one fittings file
---------------------------------------

YAML allows for multiple documents to be assembled in one fittings plan.
The separation of documents is done with three dashes at the beginning of a line.
The first document is reserved for plumbery parameters, default settings, etc.
Therefore the description of blueprints starts on the second document:

.. sourcecode:: yaml

    ---
    information:
      - "NFS client and server at two different data centres"

    ---
    blueprints:
      ...

Deploying in multiple geographies
---------------------------------

Since Plumbery processes each document independently, it is really easy to configure
a deployment that spans multiple data centres, like in the following example:

.. sourcecode:: yaml

    ---
    information:
      - "Multi-Geography deployment example"
    ---
    regionId: dd-eu
    locationId: EU6
    blueprints:
      ...
    ---
    regionId: dd-na
    locationId: NA9
    blueprints:
      ...

Combining private and public clouds in a deployment
---------------------------------------------------

Private MCPs are set using the apiHost parameter, you must also include the datacenter ID of the cloud as the locationId.
You can then include another document(s) with the public cloud fittings:

.. sourcecode:: yaml

    ---
    information:
      - "Multi-Geography deployment example"
    ---
    apiHost: my-private-cloud.com
    locationId: MY1
    blueprints:
      ...
    ---
    regionId: dd-na
    locationId: NA9
    blueprints:
      ...

Complete example
----------------

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


