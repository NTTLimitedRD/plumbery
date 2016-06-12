Getting Started
===============

Are you looking for a kind plumber to assist you in daily cloud deployment and
operations? Here is the most vital information that you need to install and
to use the software.

You need pip, a package management system, to install some of the modules used in this document.
Should your system not have pip installed, run this command:

.. sourcecode:: bash

    $ sudo apt-get install python-pip

Install Apache Libcloud
-----------------------

The orchestration of cloud services is a hot topic these days. Apache
Libcloud is evolving swiftly thanks to many contributions. For this reason,
you are encouraged to install the development version of the library:

.. sourcecode:: bash

    $ sudo pip install -e git+https://git-wip-us.apache.org/repos/asf/libcloud.git@trunk#egg=apache-libcloud

This version is the one used by Plumbery, and it may be more advanced than
the stable version of Apache Libcloud.

Install the plumbery package
----------------------------

Plumbery is available as a python package, so the installation, the upgrade,
and the removal of the software are really easy.

Install the plumbery package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plumbery is `available on PyPi`_. You can install latest stable version using pip:

.. sourcecode:: bash

    $ sudo apt-get install python-pip python-dev
    $ sudo pip install plumbery

The installation of `python-dev` is required for the installation of the module
`netifaces`, that is used by Plumbery to get information about network interfaces.

For installation on Windows, you may need to first install the Python Compiler for VC++. https://www.microsoft.com/en-us/download/confirmation.aspx?id=44266
Note this only works for Python 2.7. If you get an error on installation saying "error: Unable to find vcvarsall.bat" this indicates you need to install this package.

.. sourcecode:: powershell
     
    $ C:\Python27\Scripts\virtualenv.exe .
    $ .\Script\pip install plumbery

Upgrade the plumbery package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the following command to retrieve the version of plumbery that has been
installed on a computer:

.. sourcecode:: bash

    $ python -m plumbery -v

You can compare this information with reference information posted at
`Plumbery package at PiPy`_. If you have used pip to install the software,
then you can use it again to upgrade the package:

.. sourcecode:: bash

    $ sudo pip install --upgrade plumbery

Remove the plumbery package
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Why would you bother about a small set of files at a computer? Anyway, if needed
here is the command to remove Plumbery from a python environment:

.. sourcecode:: bash

    $ sudo pip uninstall plumbery

If you need the full development environment
--------------------------------------------

Maybe you want to upgrade the on-line documentation of Plumbery. For this
you have to edit the `.rst` files that are in the `docs` directory. Or you
want to add a new polisher in `plumbery\polishers`, for a new or special usage.
Or you would like to troubleshoot an issue and put some `print()` statements in
the code. And why not fix a bug or even implement a new feature?

In all these situations, you would like to get a full copy of all files, and
change them at will on your own computer.

Install the plumbery development environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some precautions are needed if you really want to contribute to the Plumbery project.
This is not really difficult, if you follow comprehensive instructions provided
at :doc:`contributing`

On the other hand, to dump a full copy of the software then you can clone
the latest development version from `Plumbery repository at GitHub`_:

.. sourcecode:: bash

    $ sudo apt-get install python-pip python-dev git
    $ sudo pip install -e git+https://github.com/bernard357/plumbery.git#egg=plumbery

Remove the plumbery development environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Type the following command to clean the python runtime:

.. sourcecode:: bash

    $ python setup.py develop --uninstall

Then you have to go back to the directory where plumbery was downloaded,
and remove files by yourself.

Configure and test your installation
------------------------------------

This section describes the standard workflow which you follow when working
with Plumbery.

Put secrets into local environment (Linux)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default Plumbery reads credentials and other secrets from the environment
of the computer where it is running.

If you are running Ubuntu you could do:

.. sourcecode:: bash

    $ nano ~/.bash_profile

and type text like the following:

.. sourcecode:: bash

    # credentials to access cloud resources from Dimension Data
    export MCP_USERNAME='*** your account name here ***'
    export MCP_PASSWORD='*** your password here ***'

    # password to access nodes remotely
    export SHARED_SECRET='*** password to access nodes ***'

Put secrets into local environment (Windows)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default Plumbery reads credentials and other secrets from the environment
of the computer where it is running.

Download https://raw.githubusercontent.com/bagder/ca-bundle/master/ca-bundle.crt into %APPDATA%\libcloud

.. sourcecode:: powershell
    
    [Environment]::SetEnvironmentVariable("MCP_USERNAME", "myusername", "Process")
    [Environment]::SetEnvironmentVariable("MCP_PASSWORD", "mypassword!", "Process")
    [Environment]::SetEnvironmentVariable("SSL_CERT_FILE", "C:\Users\Anthony\AppData\Roaming\libcloud\ca-bundle.crt", "Process")


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


Check your installation with demonstration files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the ``demos`` directory that is coming with the plumbery development
environment you will find a reference ``fittings.yaml`` file. Else you
can `download the reference fittings plan`_ and use it at will.

To check your installation, you would like to ask plumbery to build a first
inventory of your fittings:

.. sourcecode:: bash

    $ cd demos
    $ python -m plumbery fittings.yaml inventory

If plumbery reports interactively where it is plumbing and what it is doing,
then your installation is working great. Congratulations!

Then your next ambition may be to pass through a full life cycle, for example
with the following command:

.. sourcecode:: bash

    $ ./sql_lifecycle.sh

This program creates multiple resources, configures them, starts and stops them,
then destroys everything. It takes about 30 minutes to execute in total. A lot
of information is reported on screen, so you have the ability to monitor what
Plumbery is doing, and to understand any problem eventually.

.. _`available on PyPi`: https://pypi.python.org/pypi/plumbery
.. _`Plumbery package at PiPy`: https://pypi.python.org/pypi/plumbery
.. _`Plumbery repository at GitHub`: https://github.com/bernard357/plumbery
.. _`download the reference fittings plan`: https://raw.githubusercontent.com/bernard357/plumbery/master/demos/fittings.yaml


