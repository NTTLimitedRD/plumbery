Configure nodes with cloud-config
=================================

Cloud-config directives are a mean to configure individual nodes via a process named cloud-init.
Cloud-init is a package that is available for major versions of Linux, including Ubuntu, CentOS, Red Hat.

On this page we will present format and usage of some useful directives that can be integrated in fittings plan handled by plumbery.

cloud-config directives and plumbery
------------------------------------

Cloud-config directive is written in YAML, like the rest of fittings plan that
plumbery is using. The cloud-config format implements a declarative syntax for many common
configuration items, making it easy to accomplish many tasks. It also allows you
to specify arbitrary commands for anything that falls outside of the predefined
declarative capabilities.

This "best of both worlds" approach lets the directive acts like a configuration
file for common tasks, while maintaining the flexibility of a script for more
complex functionality:

.. sourcecode:: yaml

  nodes:

    - myServer:
       cloud-config:
         users:
           - name: demo
             groups: sudo
             shell: /bin/bash
             sudo: ['ALL=(ALL) NOPASSWD:ALL']
             ssh-authorized-keys:
               - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDf0q4PyG0doiBQYV7OlOxbRjle026hJPBWD+eKHWuVXIpAiQlSElEBqQn0pOqNJZ3IBCvSLnrdZTUph4czNC4885AArS9NkyM7lK27Oo8RV888jWc8hsx4CD2uNfkuHL+NI5xPB/QT3Um2Zi7GRkIwIgNPN5uqUtXvjgA+i1CS0Ku4ld8vndXvr504jV9BMQoZrXEST3YlriOb8Wf7hYqphVMpF3b+8df96Pxsj0+iZqayS9wFcL8ITPApHi0yVwS8TjxEtI3FDpCbf7Y/DmTGOv49+AWBkFhS2ZwwGTX65L61PDlTSAzL+rPFmHaQBHnsli8U9N6E4XHDEOjbSMRX user@example.com
               - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDcthLR0qW6y1eWtlmgUE/DveL4XCaqK6PQlWzi445v6vgh7emU4R5DmAsz+plWooJL40dDLCwBt9kEcO/vYzKY9DdHnX8dveMTJNU/OJAaoB1fV6ePvTOdQ6F3SlF2uq77xYTOqBiWjqF+KMDeB+dQ+eGyhuI/z/aROFP6pdkRyEikO9YkVMPyomHKFob+ZKPI4t7TwUi7x1rZB1GsKgRoFkkYu7gvGak3jEWazsZEeRxCgHgAV7TDm05VAWCrnX/+RzsQ/1DecwSzsP06DGFWZYjxzthhGTvH/W5+KFyMvyA+tZV4i1XM+CIv/Ma/xahwqzQkIaKUwsldPPu00jRN user@desktop
         runcmd:
           - touch /test.txt

This example allows us to illustrate a number of important things.

First, each cloud-config directive begins with a standalone ``cloud-config:`` key.
This signals plumbery that this should be handled as a cloud-config file, and communicated to the target node.

The directive above has two top-level directives, ``users`` and ``runcmd``.
These both serve as keys. The values of these keys consist of all of the indented lines after the keys.

In the case of the users key, the value is a single list item. We know this because
the next level of indentation is a dash (-) which specifies a list item, and because
there is only one dash at this indentation level. In the case of the users directive,
this incidentally indicates that we are only defining a single user named ``demo``.

The list item itself contains an associative array with more key-value pairs.
These are sibling elements because they all exist at the same level of indentation.
Each of the user attributes are contained within the single list item we described above.

Some things to note are that the strings you see do not require quoting and that
there are no unnecessary brackets to define associations. The interpreter can
determine the data type fairly easily and the indentation indicates the relationship of items, both for humans and programs.

Plumbery will push the cloud-config directive to target nodes with the following
command::

  python -m plumbery fittings.yaml prepare

By now, you should have a working knowledge of the YAML format and feel comfortable
working with information using the rules we discussed above.
We can now begin exploring some of the most common directives for cloud-config.

Write files to the file system
------------------------------

In order to write files to the disk, you should use the ``write_files`` directive.

Each file that should be written is represented by a list item under the directive.
These list items will be associative arrays that define the properties of each file.

The only required keys in this array are path, which defines where to write the file,
and content, which contains the data you would like the file to contain.

The available keys for configuring a write_files item are:

- **path:** The absolute path to the location on the filesystem where the file should be written.

- **content:** The content that should be placed in the file.
  For multi-line input, you should start a block by using a pipe character (|)
  on the "content" line, followed by an indented block containing the content.
  Binary files should include "!!binary" and a space prior to the pipe character.

- **permissions:** The octal permissions set that should be given for this file.

- **encoding:** An optional encoding specification for the file.
  This can be "b64" for Base64 files, "gzip" for Gzip compressed files,
  or "gz+b64" for a combination. Leaving this out will use the default, conventional file type.

For example, we could write a file to /test.txt with the contents::

  Hello world.
  How are you doing today?

The portion of the cloud-config that would accomplish this would look like this:

.. sourcecode:: yaml

  cloud-config:
    write_files:
      - path: /test.txt
        content: |
          Hello world.
          How are you doing today?

Update or install packages on the server
----------------------------------------

To install additional packages, you can simply list the package names using the
``packages:`` directive. Each list item should represent a package:

.. sourcecode:: yaml

  cloud-config:
    packages:
      - nodejs
      - npm
      - nodejs-legacy
      - mongodb
      - mongodb-server
      - git

One advantage of using cloud-config to install packages is that this directive
will function with either yum or apt managed distributions.

Run shell commands as root
--------------------------

If none of the managed actions that cloud-config provides works for what you
want to do, you can also run arbitrary commands with the ``runcmd:`` directive.
This directive takes a list of items to execute, that will be passed to the shell process:

.. sourcecode:: yaml

  cloud-config:
    runcmd:
      - echo "===== Installing Docker"
      - curl -sSL https://get.docker.com/ | sh

Any output will be written to the ``/var/log/cloud-init-output.log`` file. This
is the file to check after any contextualisation attempt, for any error eventually.

Preserve passwords and root access
----------------------------------

The original cloud-init package disables ssh access for the root account. It also
changes the server configuration to prevent authentication with passwords, and
allow ssh keys only.

You can ask plumbery to generate keys and transmit these to nodes to fully
secure nodes and to support passwordless access to nodes.

However, for simple demonstrations, or similar short-lived deployments, you
may just add following directives to access nodes with ssh, as root, with the
master secret password used by plumbery for the creation of servers:

.. sourcecode:: yaml

  cloud-config:
    disable_root: false
    ssh_pwauth: true

Deploying at two data centres
-----------------------------

Plumbery supports multiple documents in a single fittings file, each document (seperated by 3 dashes in YAML) can have it's own regionId and locationId.

.. sourcecode:: yaml

    ---
    information:
      - "Multi-Geography deployment example"
    links:
      documentation: https://developer.dimensiondata.com/PLUM
    ---
    regionId: dd-eu
    locationId: EU6
    blueprints:
      ...
    ---
    regionId: dd-na
    locationId: NA9
    blueprints:
      ...

How to learn more about cloud-config?
-------------------------------------

Since cloud-config has become an industry-standard, that is used commonly at Amazon Web Services,
at OpenStack-based clouds, and others, you will find many interesting web
pages and tutorials on the Internet, for example::

  http://cloudinit.readthedocs.org/en/latest/topics/examples.html

Here you will learn how to use chef or puppet with cloud-config, install ssh keys,
and many more interesting things.

