Installing plumbery on Linux and Mac OSX
========================================

The setup process on these operating systems is really quick. At the end of the process, you will be in a position to control your infrastructure at any Managed Cloud Control (MCP) of Dimension Data.


Check python
------------

It is likely that your system already has python 2.7. Run this in a terminal window::

    $ python -v

If the system complains that the directory does not exist, or that it can not find python, then some extra steps are qrequired. Go to the following address to get more support::

    http://python.org/download/releases/2.7/

On the other hand, if you get a proper version number, which is very likely, then you can exit the interpreter and move to the next step::

    >>>exit()
    >


Install pip
-----------

You need pip, a package management system, to install modules related to plumbery.


On Ubuntu and Debian systems, run this command:

.. sourcecode:: bash

    $ sudo apt-get install python-pip python-dev

On Red Hat and CentOS systems, do::

    $ sudo yum install python-pip python-dev

On Mac OSX, install Homebrew first, then use it for the setup of pip::

    $ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    $ brew install python-pip python-dev

To check pip you can get a full list of packages that have been installed on your workstation::

    $ pip freeze


Install apache-libcloud
-----------------------

Now that building blocks have put together, we will pull Apache Libcloud and install it locally.
Go the directory where pip executable has been put, and ask it to install Apache Libcloud::

    $ pip install apache-libcloud


Install plumbery
----------------

Plumbery is a regular python package that has been made `available on PyPi`_.
So it is a no-brainer to install it with pip::

    $ pip install plumbery

Test your installation
----------------------

The following command loads plumbery and ask it to display its version number::

    $ python -m plumbery -v


Set run-time environment variables
----------------------------------

By default Plumbery reads credentials and other secrets from the environment
of the computer where it is running.

Following system variables are expected by plumbery:

* ``MCP_USERNAME`` - This is the user name that you use to connect to CloudControl

* ``MCP_PASSWORD`` - This is the password that you enter in CloudControl

* ``SHARED_SECRET`` - This is the admin/root password that is communicated to new servers created over the API.
  You should select a long and difficult pass phrase.


If you are running Ubuntu or Mac OSX you could do::

    $ nano ~/.bash_profile

and type text like the following::

    # credentials to access cloud resources from Dimension Data
    export MCP_USERNAME='*** your account name here ***'
    export MCP_PASSWORD='*** your password here ***'

    # password to access nodes remotely
    export SHARED_SECRET='*** password to access nodes ***'

Then close all terminal windows, and re-open one to ensure that environment variables have been updated.

Run first deployment
--------------------

Open your preferred text editor to create a new file named ``fittings.yaml``.
Put the following content in it, save the file, and close the editor:

.. sourcecode:: yaml

    locationId: EU6

    blueprints:

      - myBluePrint:
          domain:
            name: myDC
          ethernet:
            name: myVLAN
            subnet: 10.11.12.0
          nodes:
            - myServer:
                appliance: 'Ubuntu'

This is a very limited configuration file, yet it is all you need to deploy a new
server in the data centre of Frankfurt in Germany (Europe).

At this stage you are ready to deploy the configuration file. The most straightforward command::

    $ python -m plumbery fittings.yaml deploy

This will display a sequence of messages so that you can monitor what is done, and check that all steps are executed correctly.

If plumbery complains about some missing variable, then close all command shells and re-open a new one so that it gets updated environment variables.

If you hit an issue that you cannot explain, then make plumbery more verbose with the debug flag::

    $ python -m plumbery fittings.yaml deploy -d

In the end, keep in mind that resources deployed by plumbery are costing money to someone!
Hopefully, there is a simple way to stop the bill::

    $ python -m plumbery fittings.yaml dispose

Congratulations! Plumbery has been installed and tested successfully!



.. _`available on PyPi`: https://pypi.python.org/pypi/plumbery
.. _`Plumbery package at PiPy`: https://pypi.python.org/pypi/plumbery
.. _`Plumbery repository at GitHub`: https://github.com/bernard357/plumbery
.. _`download the reference fittings plan`: https://raw.githubusercontent.com/bernard357/plumbery/master/demos/fittings.yaml


