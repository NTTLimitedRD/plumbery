Getting Started
===============

Are you looking for a kind plumber to assist you in daily cloud deployment and
operations? Here is the most vital information that you need to install and
to use the software.

Install stable version
----------------------

Plumbery is available on PyPi. You can install latest stable version using pip:

.. sourcecode:: bash

    $ sudo apt-get install python-pip python-dev
    $ sudo pip install plumbery

The installation of python-dev is required for the installation of the module
netifaces, that is used by Plumbery to get information about network interfaces.

Install development version
---------------------------

You can install latest development version from our Git repository:

.. sourcecode:: bash

    $ sudo apt-get install python-pip python-dev git
    $ sudo git clone https://github.com/bernard357/plumbery.git
    $ cd plumbery
    $ python setup.py install

Upgrade
-------

If you used pip to install the software then you can also use it to upgrade it:

.. sourcecode:: bash

    $ sudo pip install --upgrade plumbery

Configure and test your installation
------------------------------------

This section describes the standard workflow which you follow when working
with Plumbery.

Put secrets into local environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default Plumbery reads credentials and other secrets from the environment
of the computer where it is running.

If you are running Ubuntu you could do:

.. sourcecode:: bash

    nano ~/.bash_profile

and type text like the following:

.. sourcecode:: bash

    # credentials to access cloud resources from Dimension Data
    export MCP_USERNAME='*** your account name here ***'
    export MCP_PASSWORD='*** your password here ***'

    # password to access nodes remotely
    export SHARED_SECRET='*** password to access nodes ***'


Prepare your fittings plan
~~~~~~~~~~~~~~~~~~~~~~~~~~

Since infrastructure is code, your first task is to document your target
deployment into a text file. In the context of Plumbery, this is called
the fittings plan, and it is usually put into a file named ``fittings.yaml``.

With that in hands, you can then use Plumbery to act on the infrastructure and
on nodes. The engine has built-in code to cover the full life cycle:

* build the infrastructure and configure it
* build nodes
* start nodes
* polish nodes -- this is to say that some processing is applied to each node
* stop nodes
* destroy nodes
* destroy the infrastructure and release all resources


Check your installation with a demonstration program
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the ``demos`` directory that is coming with Plumbery you will find a
reference ``fittings.yaml`` file, plus many programs that are using Plumbery.

To check your installation, you would like to pass through a full life cycle
with the following command:

.. sourcecode:: bash

    $ ./sql_lifecycle.sh

This program creates multiple resources, configures them, starts and stops them,
then destroys everything. It takes about 30 minutes to execute in total. A lot
of information is reported on screen, so you have the ability to monitor what
Plumbery is doing, and to understand any problem eventually.


Use Plumbery as a python library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since Plumbery is easy to load, you can use it interactively like in the
following example:

.. sourcecode:: python

    >>>from plumbery.engine import PlumberyEngine
    >>>PlumberyEngine('fittings.yaml').build_blueprint('beachhead control')
    ...

As a next step, you are encouraged to have a deep look at the various files
put in the ``demos`` directory. There is a sophisticated ``fittings.yaml`` file
that demonstrates most advanced features supported by Plumbery. Many python
snippets are provided as well.

