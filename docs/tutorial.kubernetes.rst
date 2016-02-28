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

.. literalinclude:: ../demos/kubernetes.yaml
   :language: yaml
   :linenos:


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

