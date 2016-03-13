========================
Ubuntu graphical desktop
========================

While Linux practitioners commonly use the command line to play with servers,
they are cases where a good graphical interface is making life far easier.
In this tutorial a Ubuntu server is deployed, then a desktop is added, then
remote graphical access is provided with VNC.

We also want to add a password to the VNC server, and to tunnel the traffic
in SSH to prevent eyesdropping.

Requirements for this use case
------------------------------

* Add a Network Domain
* Add an Ethernet network
* Deploy a Ubuntu server
* Monitor this server
* Assign a public IPv4 address
* Add address translation to ensure end-to-end IP connectivity
* Add firewall rule to accept TCP traffic on port 22 (ssh)
* Install Ubuntu gnome-based desktop
* Install VNC server
* Configure VNC as a service

Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. code-block:: yaml
   :linenos:

    ---
    locationId: NA12
    regionId: dd-na

    blueprints:

      - ubuntu:

          domain:
            name: UbuntuFox
            service: essentials
            ipv4: 2

          ethernet:
            name: ubuntufox.servers
            subnet: 192.168.20.0

          nodes:

            - ubuntu01:

                appliance: 'Ubuntu 14'
                cpu: 2
                memory: 8
                monitoring: essentials
                glue:
                  - internet 22 5901

                information:
                  - "secure your connection: ssh -L 5901:127.0.0.1:5901 root@{{ node.public }}"
                  - "open a VNC viewer at 127.0.0.1:5901 to access the desktop"
                  - "enter password {{ vnc.secret }} when asked"

                cloud-config:
                  disable_root: false
                  ssh_pwauth: True
                  packages:
                    - ntp
                    - expect
                    - ubuntu-desktop
                    - gnome-session-fallback
                    - vnc4server

                  write_files:

                    - path: /root/.vnc/set_password
                      permissions: "0700"
                      content: |
                            #!/bin/sh
                            export USER="root"
                            export HOME="/root"
                            /usr/bin/expect <<EOF
                            spawn "/usr/bin/vncpasswd"
                            expect "Password:"
                            send "{{ vnc.secret }}\r"
                            expect "Verify:"
                            send "{{ vnc.secret }}\r"
                            expect eof
                            exit
                            EOF

                    - path: /root/.vnc/xstartup
                      permissions: "0755"
                      content: |
                            #!/bin/sh

                            export XKL_XMODMAP_DISABLE=1
                            unset SESSION_MANAGER
                            unset DBUS_SESSION_BUS_ADDRESS

                            [ -x /etc/vnc/xstartup ] && exec /etc/vnc/xstartup
                            [ -r $HOME/.Xresources ] && xrdb $HOME/.Xresources
                            xsetroot -solid grey
                            vncconfig -iconic &

                            gnome-session &
                            gnome-panel &
                            gnome-settings-daemon &
                            metacity &
                            nautilus &
                            gnome-terminal &

                    - path: /etc/init.d/vncserver
                      permissions: "0755"
                      content: |
                            #!/bin/bash
                            ### BEGIN INIT INFO
                            # Provides: tightvncserver
                            # Required-Start:
                            # Required-Stop:
                            # Default-Start: 2 3 4 5
                            # Default-Stop: 0 1 6
                            # Short-Description: start vnc server
                            # Description:
                            ### END INIT INFO

                            export USER="root"
                            export HOME="/root"

                            . /lib/lsb/init-functions

                            case "$1" in
                            start)
                                echo "Starting vncserver on :1"
                                vncserver :1 -geometry 1280x800 -depth 24
                            ;;

                            stop)
                                echo "Stopping vncserver on :1"
                                vncserver -kill :1
                            ;;

                            restart)
                                $0 stop
                                $0 start
                            ;;
                            *)
                                echo "Usage: $0 {start|stop|restart}"
                                exit 1
                            esac
                            exit 0

                  runcmd:
                    - /root/.vnc/set_password
                    - update-rc.d vncserver defaults
                    - /etc/init.d/vncserver restart

Some interesting remarks on this fittings plan:

**expect** - The password used by VNC server is normally entered interactively.
Here the package ``expect`` has been added, with a little script, to automate
this interactivity. This is a very powerful mechanism that can be useful
in various situations.

**Service installation** - The VNC server is installed as an ordinary service via an additional command
in `/etc/init.d/` and  with `update-rc.d`

**Infrastructure documentation** - The ``information:`` directive provides
comprehensive instructions to finalise the setup. This is displayed at the end
of the command ``deploy``. It can also be retrieved unattended with the
command ``information``.


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

Of course, you need a VNC viewer on your computer to make it work. As a starting
point you can attempt to enter the following URL in a browser window::

    vnc://127.0.0.1:5901

Destruction commands
--------------------

The more servers you have, the more costly it is. Would you like to stop the
invoice?

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml dispose

