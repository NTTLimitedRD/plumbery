==========================================
Multiple disks combined in logical volumes
==========================================

The Managed Cloud Platform from Dimension Data can accomodate for sophisticated
storage needs. In this tutorial we show how to add 6 virtual disks to a single
node, and how to combine these resources in 3 convenient logical volumes.

Requirements for this use case
------------------------------

* Add a Network Domain
* Add an Ethernet network
* Deploy a Ubuntu server
* Add disk 1 with 100 GB of standard storage
* Add disk 2 with 200 GB of standard storage
* Add disk 3 with 30 GB of high-performance storage
* Add disk 4 with 40 GB of high-performance storage
* Add disk 5 with 1000 GB of economy storage
* Add disk 6 with 1000 GB of economy storage
* Monitor this server in the real-time dashboard
* Assign a public IPv4 address
* Add address translation to ensure end-to-end IP connectivity
* Add firewall rule to accept TCP traffic on port 22 (ssh)
* Partition each disk as of Linux LVM type (8e)
* Use LVM to manage logical storage provided by multiple disks
* Extend the mount / with storage brought by disks 1 and 2
* Create new mount /highperformance with combined capacity provided by disks 3 and 4
* Create new mount /economy with combined capacity provided by disks 5 and 6
* Combine the virtual disks into a single expanded logical volume (LVM)
* Install a new SSH key to secure remote communications
* Configure SSH to reject passwords and to prevent access from root account

Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. literalinclude:: ../demos/disks.yaml
   :language: yaml
   :linenos:


Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

These commands will build fittings as per the provided plan, start the server
and bootstrap it.

You can find the public address assigned to the node like this:

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

.. sourcecode:: bash

    $ sudo fdisk -l
    $ df -h
    $ mount


These commands are self-explanatory and validate disk deployment and configuration.

Destruction commands
--------------------

Launch following command to remove all resources involved in the fittings plan:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml dispose

