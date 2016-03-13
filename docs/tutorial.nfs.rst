==============================
NFS over ipv6 back-end network
==============================

In this tutorial a NFS server is deployed at one data centre, and
a NFS client is deployed at another data centre. The infrastructure and the
nodes are configured to talk to each other over the secured ipv6 back-bone
that ties all MCP together.

Requirements for this use case
------------------------------

* Add a Network Domain at each data centre
* Add an Ethernet network at each data centre
* Allow IPv6 traffic between the two networks
* Deploy a Ubuntu server at each data centre
* Monitor these servers
* Assign a public IPv4 address to each server
* Add address translation to IPv4 connectivity from the Internet
* Add firewall rule to accept TCP traffic on port 22 (ssh)
* Add ipv6 addresses to `/etc/hosts` for easy handling
* Install NFS back-end software on server node
* Install NFS client software on client node
* At the client node, change `/etc/fstab` to mount NFS volume automatically
* From the client node, write a `hello.txt` to the server

Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. code-block:: yaml
   :linenos:

    ---
    locationId: AU10
    regionId: dd-au

    blueprints:

      - nfs:

          domain:
            name: NfsFox
            description: "Demonstration of NFS - server side"
            ipv4: 2

          ethernet:
            name: nfsfox.servers
            subnet: 192.168.20.0
            accept:
              - AU11::nfsfox.servers

          nodes:

            - nfsServer:

                appliance: 'Ubuntu 14'
                cpu: 2
                memory: 8
                monitoring: essentials
                glue:
                  - internet 22
                information:
                  - "this is the NFS server"
                  - "ssh root@{{ nfsServer.public }}"
                  - "check service with: showmount -e nfsServer"
                cloud-config:
                  disable_root: false
                  ssh_pwauth: True
                  packages:
                    - ntp
                    - nfs-kernel-server
                  write_files:
                    - path: /etc/exports
                      content: |
                            /var/nfs    *(rw,sync,no_subtree_check)

                    - path: /root/hosts.awk
                      content: |
                        #!/usr/bin/awk -f
                        /^{{ nfsServer.ipv6 }}/ {next}
                        /^{{ AU11::nfsClient.ipv6 }}/ {next}
                        {print}
                        END {
                         print "{{ nfsServer.ipv6 }}    nfsServer"
                         print "{{ AU11::nfsClient.ipv6 }}    nfsClient"
                        }

                  runcmd:
                    - cp -n /etc/hosts /etc/hosts.original
                    - awk -f /root/hosts.awk /etc/hosts >/etc/hosts.new && mv /etc/hosts.new /etc/hosts
                    - mkdir /var/nfs
                    - chown nobody:nogroup /var/nfs
                    - exportfs -a
                    - service nfs-kernel-server start

    ---
    locationId: AU11
    regionId: dd-au

    blueprints:

      - nfs:

          domain:
            name: NfsFox
            description: "Demonstration of NFS - client side"
            ipv4: 2

          ethernet:
            name: nfsfox.servers
            subnet: 192.168.20.0
            accept:
              - AU10::nfsfox.servers

          nodes:
            - nfsClient:
                appliance: 'Ubuntu 14'
                monitoring: essentials
                glue:
                  - internet 22
                information:
                  - "this is the NFS client, with automatic mount to the server"
                  - "ssh root@{{ nfsClient.public }}"
                  - "check connectivity to server with: showmount -e nfsServer"
                  - "check actual service with: mount -t nfs"
                cloud-config:
                  disable_root: false
                  ssh_pwauth: True
                  packages:
                    - ntp
                    - nfs-common
                  write_files:
                    - path: /root/hosts.awk
                      content: |
                        #!/usr/bin/awk -f
                        /^{{ AU10::nfsServer.ipv6 }}/ {next}
                        /^{{ nfsClient.ipv6 }}/ {next}
                        {print}
                        END {
                         print "{{ AU10::nfsServer.ipv6 }}    nfsServer"
                         print "{{ nfsClient.ipv6 }}    nfsClient"
                        }

                    - path: /root/fstab.awk
                      content: |
                        #!/usr/bin/awk -f
                        !/nfsServer/
                        END {
                         print "nfsServer:/var/nfs    /shared-nfs   nfs auto,noatime,nolock,bg,nfsvers=4,intr,actimeo=1800 0 0"
                        }

                  runcmd:
                    - cp -n /etc/hosts /etc/hosts.original
                    - awk -f /root/hosts.awk /etc/hosts >/etc/hosts.new && mv /etc/hosts.new /etc/hosts
                    - mkdir -p /shared-nfs
                    - cp -n /etc/fstab /etc/fstab.original
                    - awk -f /root/fstab.awk /etc/fstab >/etc/fstab.new && mv /etc/fstab.new /etc/fstab
                    - mount -a
                    - df -h
                    - echo "hello world written by nfsClient" >/shared-nfs/hello.txt

Some interesting remarks on this fittings plan:

**IPv6 connectivity** - In this case we can see that network names and
private IPv4 subnets are exactly the same at both data centres. In other terms,
we don't need IPv4 to be routable across the two locations. We use IPv6 instead,
and plumbery helps to orchestrate the long addresses that are coming with this
protocol.

**etc/hosts** - The update of `etc/hosts` is made by a script in AWK language.
The script is built dynamically by plumbery, based on actual addresses assigned
to nodes. Since each data centre is described in a separate YAML document of
the fittings plan, there is a special syntax to designate remote networks and
nodes. At `AU10`, the remote network is designated by `AU11::nfsfox.servers`
and the NFS client by `AU11::nfsClient`. This is creating name spaces that can
be geographically consistent across global deployments.

**etc/fstab** - On the client side there is an example of AWK script to modify `etc/fstab`
dynamically. Therefore, if the node is rebooted it will reconnect
automatically.

Deployment commands
-------------------

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

This command will build fittings as per the provided plan, start the server
and bootstrap it.

Follow-up commands
------------------

You can find instructions to connect, including IP addresses to use, like this:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml information

The best is to go to the NFS server via ssh, and to read the file written by
the NFS client in `/var/nfs`.

Destruction commands
--------------------

The more servers you have, the more costly it is. Would you like to stop the
invoice?

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml dispose

