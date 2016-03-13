======================
File server with Samba
======================

This tutorial is aiming to install a standalone Samba server to share
files among multiple users.

Requirements for this use case
------------------------------

* Create a Network Domain
* Create an Ethernet network (a VLAN)
* Deploy a virtual server
* Add the server to the automated monitoring dashboard
* Assign a public IPv4 address to the server
* Add address translation to ensure end-to-end IP connectivity
* Add firewall rule to accept TCP traffic on ports 22 (ssh), 139 and 445
* Add samba to the server and configure it


Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. code-block:: yaml
   :linenos:

    ---
    locationId: NA12
    regionId: dd-na

    blueprints:

      - samba:

          domain:
            name: SambaFox
            service: essentials
            ipv4: 2

          ethernet:
            name: sambafox.servers
            subnet: 192.168.20.0

          nodes:

            - samba01:

                appliance: 'Ubuntu 14'
                cpu: 2
                memory: 4
                monitoring: essentials
                glue:
                  - internet 22 139 445

                information:
                  - "connect to smb://{{ node.public }}/ to write and read files"

                cloud-config:
                  disable_root: false
                  ssh_pwauth: true
                  packages:
                    - ntp
                    - samba
                    - samba-common
                    - python-glade2
                    - system-config-samba
                  write_files:
                    - path: /etc/samba/smb.conf.plumbery
                      content: |
                        [global]
                        workgroup = WORKGROUP
                        server string = Samba Server %v
                        netbios name = {{ node.name }}
                        load printers = no
                        printing = bsd
                        printcap name = /dev/null

                        [Public]
                        comment = Public share access
                        path = /samba/public
                        browsable = yes
                        writable = yes
                        guest ok = yes
                        read only = no
                        force user = nobody
                        force group = nogroup

                  runcmd:
                    - mkdir -p /samba/public
                    - chmod -R 0755 /samba/public
                    - chown -R nobody:nogroup /samba/public/
                    - cp -n /etc/samba/smb.conf /etc/samba/smb.conf.original
                    - rm /etc/samba/smb.conf
                    - cp /etc/samba/smb.conf.plumbery /etc/samba/smb.conf
                    - service smbd restart



Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy
    $ python -m plumbery fittings.yaml start

This command will build fittings as per the provided plan, start the server
and bootstrap it. Look at messages displayed by plumbery while it is
working, so you can monitor what's happening.

Connect to the server and share files
-------------------------------------

.. note::
  This use case does not work yet. The deployment itself is ok, yet the
  SMB connection to the server is failing. Thanks for your contribution
  on troubleshooting the use case and make it work.

Destruction commands
--------------------

Cloud computing has a hard rule. Any resource has a cost, be it used or not.
At the end of every session, you are encouraged to destroy everything.
Hopefully, plumbery is making this really simple:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy

