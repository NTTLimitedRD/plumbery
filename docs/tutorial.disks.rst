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

.. code-block:: yaml
   :linenos:

    ---

    defaults:

      cloud-config: # default for all nodes created by plumbery

        ssh_keys: # generated randomly, and used on subsequent invocations
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

          - name: root
            ssh-authorized-keys:
              - "{{ key.rsa_public }}"
              - "{{ local.rsa_public }}"

        disable_root: false

        ssh_pwauth: false

    ---

    locationId: NA12

    blueprints:

      - disks:

          domain:
            name: DisksFox
            ipv4: auto
          ethernet:
            name: DisksNetwork
            subnet: 10.0.0.0
          nodes:

            - disks01:

                information:
                  - "6 disks have been added to this node"
                  - "2 first disks extend standard storage coming with system disk"
                  - "2 next disks are combined in a logical volume for high-performance storage"
                  - "2 last disks are combined in a logical volume for economy storage"
                  - "connect to this server in a terminal window:"
                  - "$ ssh ubuntu@{{ node.public }}"
                  - "check disk drives with:"
                  - "$ sudo fdisk -l"
                  - "$ df -h"
                  - "$ mount"

                cpu: 2
                memory: 2

                # manage disks of this node
                #
                disks:
                  - 1 100 standard
                  - 2 200 standard
                  - 3 30 highperformance
                  - 4 40 highperformance
                  - 5 1000 economy
                  - 6 1000 economy

                glue:
                  - internet 22
                monitoring: essentials

                cloud-config:

                  packages:
                    - ntp

                  write_files:

                    - path: /root/set_pdisk.sh
                      content: |
                        #!/usr/bin/env bash
                        if [ ! -b ${1}1 ]; then
                        echo "===== Partioning ${1}"
                        cat <<EOF | fdisk ${1}
                        n
                        p
                        1


                        t
                        8e
                        w
                        EOF
                        echo "===== Creating LVM physical disk ${1}1"
                        pvcreate ${1}1
                        fi


                    - path: /root/set_vdisk.sh
                      content: |
                        #!/usr/bin/env bash
                        if [ -z "$(blkid ${1})" ];
                        then
                            echo "===== Formatting ${1}"
                            mkfs -t ${2} ${1}
                        fi
                        UUID=$(blkid ${1} | sed -n 's/.*UUID=\"\([^\"]*\)\".*/\1/p')

                        if ! grep -q "${UUID}" /etc/fstab; then
                            echo "===== Adding ${1} to fstab"
                            LINE="UUID=\"${UUID}\"\t${3}\t${2}\tnoatime,nodiratime,nodev,noexec,nosuid\t1 2"
                            echo -e "${LINE}" >> /etc/fstab
                        fi

                        echo "===== Mounting ${3}"
                        [ -d "${3}" ] || mkdir -p "${3}"
                        mount "${3}"

                  runcmd:
                    - chmod +x /root/set_pdisk.sh
                    - chmod +x /root/set_vdisk.sh

                    - echo "===== Handling additional disk 1"
                    - /root/set_pdisk.sh /dev/sdb
                    - echo "===== Adding /dev/sdb1 to standard storage"
                    - vgextend rootvol00 /dev/sdb1
                    - lvextend -l +100%FREE /dev/mapper/rootvol00-rootlvol00
                    - resize2fs /dev/mapper/rootvol00-rootlvol00

                    - echo "===== Handling additional disk 2"
                    - /root/set_pdisk.sh /dev/sdc
                    - echo "===== Adding /dev/sdc1 to standard storage"
                    - vgextend rootvol00 /dev/sdc1
                    - lvextend -l +100%FREE /dev/mapper/rootvol00-rootlvol00
                    - resize2fs /dev/mapper/rootvol00-rootlvol00

                    - echo "===== Handling additional disk 3"
                    - /root/set_pdisk.sh /dev/sdd
                    - echo "===== Configuring /dev/sdd1 for high-performance storage"
                    - vgcreate highperformancevg /dev/sdd1
                    - lvcreate -l 100%FREE -n highperformancelv highperformancevg
                    - /root/set_vdisk.sh /dev/highperformancevg/highperformancelv ext4 /highperformance

                    - echo "===== Handling additional disk 4"
                    - /root/set_pdisk.sh /dev/sde
                    - echo "===== Adding /dev/sde1 to high-performance storage"
                    - vgextend highperformancevg /dev/sde1
                    - lvextend -l +100%FREE /dev/mapper/highperformancevg-highperformancelv
                    - resize2fs /dev/mapper/highperformancevg-highperformancelv

                    - echo "===== Handling additional disk 5"
                    - /root/set_pdisk.sh /dev/sdf
                    - echo "===== Configuring /dev/sdf1 for economy storage"
                    - vgcreate economyvg /dev/sdf1
                    - lvcreate -l 100%FREE -n economylv economyvg
                    - /root/set_vdisk.sh /dev/economyvg/economylv ext3 /economy

                    - echo "===== Handling additional disk 6"
                    - /root/set_pdisk.sh /dev/sdg
                    - echo "===== Adding /dev/sdg1 to economy storage"
                    - vgextend economyvg /dev/sdg1
                    - lvextend -l +100%FREE /dev/mapper/economyvg-economylv
                    - resize2fs /dev/mapper/economyvg-economylv


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

