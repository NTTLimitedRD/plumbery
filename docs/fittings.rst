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

Dynamic variables
-----------------

Dynamic variables reflect values assigned by the cloud platform such as network addresses.

=======================  ======================  ================================================================================================
Variable                 Example                 Description
=======================  ======================  ================================================================================================
Self-name                {{ node.name }}         Name of the current node, e.g., Server1
Self private address     {{ node.private }}      Private IPv4 address, e.g., 10.11.2.3
Self public address      {{ node.public }}       Public IPv4 address, e.g., 8.9.10.11 -- requires the directive 'internet' to assign an address
Self IPv6 address        {{ node.ipv6 }}         IPv6 address defined for the node
Node private address     {{ server1.private }}   Private IPv4 address of server named server1
Node public address      {{ server1.public }}    Public IPv4 address -- requires the directive 'internet' as well
Node IPv6 address        {{ host357.ipv6 }}       IPv6 address defined for the node named host357
=======================  ======================  ================================================================================================

Using dynamic variables
-----------------------

Plumbery will set pre-defined attributes when asked, for example, a private IPv4 address to a node.
This is working great, and all you have to do for this is document such attributes in a fittings plan.

However in many situations you will handle information that is either created dynamically, or
that is declared outside a fittings plan.

Some examples:

* IPv6 addresses assigned automatically by the platform
* IPv4 addresses selected dynamically from subnets
* random password used for the setup of a MySQL server
* SSH keys to be created for a specific deployment

This is where you can use templating capabilities of plumbery directly in the fittings plan.

To illustrate the case we will consider a deployment with two nodes deployed in different data centres.
The nodes have to communicate over the IPv6 back-end infrastructure that connects all data centres
deployed by Dimension Data. In other terms, the IPv6 address of node-a has to be given to node-b, and
the IPv6 address of node-b has to be given to node-a.

As you can expect, the most straightforward implementation relies on the file /etc/hosts of both nodes.
This is the natural place where names and addresses can be mapped. In plumbery,
we would start with something like the following:

.. sourcecode:: yaml

    write_files:

        # map IPv6 addresses with names
        #
        - path: /etc/hosts
          content: |
             {{ node-a.ipv6 }}    node-a
             {{ node-b.ipv6 }}    node-b


Before the content of /etc/hosts is actually sent to the nodes, plumbery looks for
references to dynamic variables, and replaces them with actual values. For example:

.. sourcecode:: yaml

    write_files:

        # map IPv6 addresses with names
        #
        - path: /etc/hosts
          content: |
             2001:0db8:85a3:0:0:8a2e:370:7334    node-a
             2001:db8:85a3:8d3:1319:8a2e:370:7348    node-b


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


