==========================================
Standalone Object-Based Storage with Minio
==========================================

`Minio`_ is a minimal cloud storage server that is compatible with Amazon S3
APIs. This is useful if you need a lightweight object-based storage backend,
for example while you develop a new digital application.

Requirements for this use case
------------------------------

* Deploy at Frankfurt in Europe
* Create a Network Domain
* Create an Ethernet network (a VLAN)
* Deploy a virtual server
* Add the server to the automated monitoring dashboard
* Assign a public IPv4 address to the server
* Add address translation to ensure end-to-end IP connectivity
* Add firewall rule to accept TCP traffic on port 22 (ssh) and 8080 (minio)
* Add minio to the virtual machine and launch the service


Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. code-block:: yaml
   :linenos:

    ---
    locationId: NA12
    regionId: dd-na

    blueprints:

      - minio:

          domain:
            name: MinioFox
            ipv4: 2

          ethernet:
            name: miniofox.servers
            subnet: 192.168.20.0

          nodes:

            - minio01:

                glue:
                  - internet 22 8080

                information:
                  - "connect to this server in a terminal window: ssh root@{{ node.public }}"
                  - "then get AccessKey and SecretKey from minio banner: cat /root/minio_keys.txt"

                cloud-config:
                  disable_root: false
                  ssh_pwauth: true
                  packages:
                    - ntp
                  runcmd:
                    - su ubuntu -c "curl https://dl.minio.io/server/minio/release/linux-amd64/minio >/home/ubuntu/minio"
                    - chmod +x /home/ubuntu/minio
                    - mkdir /home/shared
                    - chown ubuntu:ubuntu /home/shared
                    - su ubuntu -c "~/minio --address {{ node.private }}:8080 server expiry 1h /home/shared" >/root/minio_keys.txt

Some notes on directives used in this fittings plan:

**Not root** - The minio server is expecting to run as user ``ubuntu``, so we are enforcing
this through the commands passed to the server.

**Interactive secrets** - The server is launched on the last command. It
generates randomly two secrets that have to be communicated to client software
and displays these on screen. Information is captured in a text file so that it
can be retrieved via a terminal session afterwards.

**Object expiration** - Server is configured to expire files after 1 hour of
storage. You can change this of course if needed.

Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

This command will build fittings as per the provided plan, start
the server, and bootstrap it. Look at messages displayed by plumbery while it is
working, so you can monitor what's happening.

Install and configure the client
--------------------------------

To actually demonstrate the service you will have to install client
software at your workstation, and configure it to access the back-end.

Minio is compatible with popular S3 tools such as ``s3cmd`` or similar.
Here we will use the Minio client, also called mc.

Instructions to install Minio client software can be found `here`_

Next step is to retrieve secrets from the server that has been deployed
by plumbery. To do this you have to connect to the server and to display
a file that was generated during the setup:

.. sourcecode:: bash

    $ ssh root@<ipv4_here>
    ...
    $ cat minio_keys.txt

In a separate terminal window you can paste the AccessKey and the SecretKey
to configure the Minio client:

.. sourcecode:: bash

    $ ./mc config host add http://<public_address>:8080 <AccessKey> <Secretkey>

Play with the service
---------------------

Ok, here is the full sequence:
* create a bucket
* copy a file from your workstation to the bucket
* generate a link to retrieve the file securely
* test the link and download the file

In other terms, type this at your workstation:

.. sourcecode:: bash

    $ ./mc mb http://<public_address>:8080/stuff
    $ ./mc cp <file> http://<public_address>:8080/stuff
    $ ./mc share download http://<public_address>:8080/stuff/

A long web link is displayed on last command. Select and copy everything,
then move to a browser window and paste everything in the top bar. Press
Enter to start the download.

You can switch to the other terminal window and check the state of the
server itself:

.. sourcecode:: bash

    $ cd /home/shared
    $ cd stuff
    $ ls

Last command should display the name of the file that you copied earlier
in the sequence.

Destruction commands
--------------------

Cloud computing has a hard rule. Any resource has a cost, be it used or not.
At the end of every session, you are encouraged to destroy everything.
Hopefully, plumbery is making this really simple:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy


.. _`Minio`: https://github.com/minio/minio/blob/master/README.md
.. _`here`: https://github.com/minio/mc