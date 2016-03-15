==============
Kubernetes pod
==============

Docker is notoriously difficult to deploy in a sophisticated environment. For
example, no routing is provided natively between containers, so you may
have to configure multiple tunnels and address translation rules to deliver
end-to-end connectivity.

By contrast, the ambition of Kubernetes is to leverage the underlying
networking infrastructure, and to provide containers at scale. Well, before
we consider the deployment of hundreds of pods, maybe it would help to start
with a single one, in order to learn.

.. image:: tutorial.kubernetes.png

In this tutorial we demonstrate how to create a class of Kubernetes nodes and
deploy one single node. Of course, you can use this file for yourself, and change it
to better accomodate your requirements.

Requirements for this use case
------------------------------

* Add a Network Domain
* Add an Ethernet network
* Deploy a large Ubuntu server
* Provide 32 CPU and 256 MB of RAM to each node
* Add a virtual disk of 100 GB
* Monitor this server in the real-time dashboard
* Assign a public IPv4 address
* Add address translation to ensure end-to-end IP connectivity
* Add firewall rule to accept TCP traffic on ssh and web ports
* Combine the virtual disks into a single expanded logical volume (LVM)
* Install a new SSH key to secure remote communications
* Configure SSH to reject passwords and to prevent access from root account
* Remove Apache
* Install Go, Docker, Calico and Kubernetes itself

Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. code-block:: yaml
   :linenos:

    ---

    defaults:

      # the same network domain is used at various facilities
      #
      domain:
        name: KubernetesFox
        description: "Kubernetes nodes"
        service: essentials
        ipv4: auto

      # the same ethernet configuration is used at various facilities
      #
      ethernet:
        name: KubernetesNetwork
        subnet: 192.168.20.0

      # default settings for a Kubernetes node
      #
      kubernetesNode:

        description: "#kubernetes #ubuntu"

        information:
          - "ssh ubuntu@{{ node.public }}"
          - "sudo su"
          - "cd /root/kubernetes"
          - "cluster/kubectl.sh get services"
          - "cluster/kubectl.sh run my-nginx --image=nginx --replicas=2 --port=80"
          - "cluster/kubectl.sh get pods"

        appliance: 'Ubuntu 14'

        # plenty of compute power
        #
        cpu: 32
        memory: 256

        # enough storage space
        #
        disks:
          - 1 100 standard

        # make the node accessible from the Internet
        #
        glue:
          - internet 22 80

        # allow for monitoring from the global dashboard
        #
        monitoring: essentials

        # contextualise this node
        #
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
                {print}
                END {
                 print "{{ node.private }}    {{ node.name }}"
                 print "{{ node.ipv6 }}    {{ node.name }}"
                }

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

            - echo "===== Cleaning packages"
            - apt-get remove apache2 -y
            - apt-get autoremove -y

            - echo "===== Installing Go"
            - apt-get install git software-properties-common gcc git -y
            - add-apt-repository ppa:evarlast/golang1.4 -y
            - apt-get update
            - apt-get install golang -y

            - echo "===== Installing Docker Engine"
            - curl -sSL https://get.docker.com/ | sh
            - usermod -aG docker ubuntu

            - echo "===== Installing Calico"
            - add-apt-repository ppa:cory-benfield/project-calico -y
            - apt-get update
            - apt-get install etcd

            - echo "===== Installing Kubernetes"
            - cd /root
            - git clone https://github.com/kubernetes/kubernetes.git
            - cd kubernetes
            - hack/local-up-cluster.sh &
            - ./build/run.sh hack/build-cross.sh

            - cluster/kubectl.sh config set-cluster local --server=http://127.0.0.1:8080 --insecure-skip-tls-verify=true
            - cluster/kubectl.sh config set-context local --cluster=local
            - cluster/kubectl.sh config use-context local

      # default settings for all nodes created by plumbery
      #
      cloud-config:

        # ask plumbery to generate a random key pair
        #
        ssh_keys:
          rsa_private: |
            {{ key.rsa_private }}
          rsa_public: "{{ key.rsa_public }}"

        # the ubuntu account will use this key as well
        #
        users:
          - default

          - name: ubuntu
            sudo: 'ALL=(ALL) NOPASSWD:ALL'
            ssh-authorized-keys:
              - "{{ key.rsa_public }}"
              - "{{ local.rsa_public }}"

        # prevent remote access from root
        #
        disable_root: true

        # force authentication with SSH key -- no password allowed
        #
        ssh_pwauth: false

    # duplicate the below to deploy another node at another location, e.g. NA12 in dd-na, etc
    #
    ---
    locationId: AU9
    regionId: dd-au

    blueprints:

      - kubernetes:
          nodes:
            - kubernetes-AU9:
                default: kubernetesNode


Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

These commands will build fittings as per the provided plan, start the server
and bootstrap it.

You can find the public address assigned to the server like this:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml information


Follow-up commands
------------------

In this use case you can use the IPv4 assigned to the node for direct ssh
connection.

.. sourcecode:: bash

    $ ssh ubuntu@<ipv4_here>


You will have to accept the new host, and authentication will be based on
the SSH key communicated to the node by Plumbery.

Then you can use the Kubernetes controller software to validate the setup:

.. sourcecode:: bash

    $ sudo su
    $ cd /root/kubernetes
    $ cluster/kubectl.sh get services
    $ cluster/kubectl.sh run my-nginx --image=nginx --replicas=2 --port=80
    $ cluster/kubectl.sh get pods

The last command should show the two instances of nginx running.

Destruction commands
--------------------

Launch following command to remove all resources involved in the fittings plan:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml dispose

