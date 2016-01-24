=======================================================
Master and slave MySQL databases in different locations
=======================================================

In this use case a master database server and a slave database server are
deployed in different locations. The back-end IPv6 infrastructure
provided by Dimension Data is used to replicate data continuously,
at no additional cost.

As shown below, plumbery provides a streamlined definition of the overall
solution, that encompasses servers location, the networking infrastructure,
the security of information flows, but also the contextualisation of nodes
and the small but important final brushes that are making a solution really
appealing.

When starting from scratch, it takes about 15 minutes to deploy the fittings
below. About half of it is related to the deployment at cloud services from
Dimension data. The other half is incurred by cloud-init in the contextualisation
of nodes, the software part of the solution.
After that time, you can connect to the cluster and use it for real.

Requirements for this use case
------------------------------

* Deploy a master database in one data centre
* Deploy a slave database in another data centre
* Create a Network Domain at each location
* Create an Ethernet network at each location
* Allow IPv6 traffic from the master network to the slave network
* Deploy a SQL server at each location
* Add servers to the automated monitoring dashboard
* Assign public IPv4 addresses to each server
* Add address translation to ensure SSH access to the nodes from the internet
* Add firewall rule to accept TCP traffic on port 22 (ssh)
* Update `etc/hosts` to bind IPv6 addresses to host names
* Manage keys to suppress passwords in SSH connections
* Install MySQL at each node
* Configure the master database
* Configure the slave database
* Populate the master database
* Dump the master database and load it at the slave node
* Start the replication from the master to the slave

Fittings plan
-------------

The plan below demonstrates multiple interesting building blocks:

* Addition of public IPv4 and firewall rules to control access to
  selected servers
* Configuration of the firewall to open communications across data centres
* Automatic registration to the monitoring services provided by Dimension Data
* Management of SSH keys to enable secured communications without passwords
* Update of etc/hosts with IPv6
* Easy templating of configuration files transmitted to nodes
* Handy generation and management of secrets required at various places
* rsync on top of ipv6 to manage heavy communications between servers
* User documentation of the infrastructure is put directly in the fittings plan

`Download this fittings plan`_ if you want to hack it for yourself. This is part of `the demonstration
directory of the plumbery project`_ at GitHub. Alternatively, you can copy the
text below and put it in a text file named ``fittings.yaml``.

.. literalinclude:: ../demos/sql.master.slave.yaml
   :language: yaml
   :linenos:

Please note that in this example both servers are exposed to public Internet.
In the real life this would probably not be the case, since database would
be accessed by application servers from within private back-end networks.

Deployment commands
-------------------

In this case, the blueprint ``sql`` is spread over two different
data centres. For this reason, plumbery will connect separately
to each data centre and to the dirty job to make you happy.

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

Since servers are up and running, you are invited to play a bit with them, and
show evidence of data replication. For example, you could open two additional
terminal windows, one for the master server and the other for the slave server.
Then connect by ssh, using the ubuntu account, and enter mysql directly.

On the master side, you can type these commands in sequence:

.. sourcecode:: sql

    use db01;
    select * from persons;
    show master status \G

Then move to the slave side, and check status of the server:

.. sourcecode:: sql

    use db01;
    select * from persons;
    show slave status \G

At this stage, the slave server should report the same GTID index than the
master.

Move back to the master server, and create a new record in the table:

.. sourcecode:: sql

    insert into persons (name) values ('Alfred');
    show master status \G

The last command should show a progress in the GTID information. How is this
reflected on slave side? There you can type the following:

.. sourcecode:: sql

    select * from persons;
    show slave status \G

The SELECT statement should reflect the record created on the other side. And
the SHOW statement should follow the evolution of the GTID on the master side.

Troubleshooting
---------------

The fittings plan is using multiple secrets, and most of them have been used
by plumbery to configure the solution dynamically. If you need to retrieve
one of these secrets, for example, the root password for SQL, then use the
following command:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml secrets

Destruction commands
--------------------

At the end of the demonstration, you may want to reduce costs with the following:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy


.. _`Download this fittings plan`: https://github.com/bernard357/plumbery/blob/master/demos/sql.master.slave.yaml
.. _`the demonstration directory of the plumbery project`: https://github.com/bernard357/plumbery/tree/master/demos