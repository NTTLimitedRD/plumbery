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

.. literalinclude:: ../demos/elk.yaml
   :language: yaml
   :linenos:


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