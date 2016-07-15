Configuring virtual disks
=========================

Plumbery has the ability to adjust virtual disks attached to a node, like in the following example:

.. sourcecode:: yaml

    nodes:

      - myServer:

          disks:

            # resize system disk to 80 GB
            #
            - 0 80

            # add a 100 GB disk for economy storage
            #
            - 1 100 economy

Components of each ``disks:`` directive
---------------------------------------

=======================  ==========  ================================================================================================
Component                 Required    Description
=======================  ==========  ================================================================================================
disk id                   yes         An integer between 0 and 9. The value 0 designates the system disk
size in GB                yes         An integer between 10 and 1000
class of storage          no          Either ``standard`` (default) or ``highperformance`` or ``economy``
=======================  ==========  ================================================================================================

How to partition and configure virtual disks?
---------------------------------------------

Any change of virtual disks made at the infrastructure level has to be reflected into the operating system itself.
For example, explicit decision is required on number and sizes of partitions.
You may want to use one file system or another, depending of requirements for the storage sub-system.
In case of storage virtualisation, there is also an option to combine multiple virtual disks in a single
logical volume and file system.

Cloud-config can be a convenient Trojan horse to perform such tasks, as demonstrated in following examples.

How to resize system disk of a Linux server?
--------------------------------------------

LVM is used for Ubuntu standard images, so the resizing of system disk is quite easy.

.. sourcecode:: yaml

      nodes:

        - myServer:

            appliance: 'Ubuntu 14'

            # augment system disk
            #
            disks:
              - 0 50 standard

            cloud-config:

              runcmd:

                - echo "===== Growing LVM with expanded disk"
                - lvextend -l +100%FREE /dev/mapper/rootvol00-rootlvol00
                - resize2fs /dev/mapper/rootvol00-rootlvol00

How to add high-performance storage on Linux?
---------------------------------------------

This case is a bit more complicated because of the partitioning, etc.
Hopefully ``cloud-config`` can help us to push some scripts to the target
node and to execute them.

.. sourcecode:: yaml

      nodes:

        - myServer:

            appliance: 'Ubuntu 14'

            # add a disk from high-performance tier of storage
            #
            disks:
              - 1 100 highperformance

            cloud-config:

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

                - echo "===== Handling additional disk"
                - chmod +x /root/set_pdisk.sh
                - /root/set_pdisk.sh /dev/sdb

                - echo "===== Configuring /dev/sdb1 for high-performance storage"
                - vgcreate highperformancevg /dev/sdb1
                - lvcreate -l 100%FREE -n highperformancelv highperformancevg
                - chmod +x /root/set_vdisk.sh
                - /root/set_vdisk.sh /dev/highperformancevg/highperformancelv ext4 /highperformance

After complete configuration, everything written to ``/highperformance`` will benefit from best performance levels.
