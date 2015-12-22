Getting Started
===============

Are you looking for a kind plumber to assist you in daily cloud deployment and
operations? Here is the most vital information that you need to install and
to use the software.

If you want to use plumbery
---------------------------

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
here is the command to remove plumbery from a python environment:

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
    $ sudo git clone https://github.com/bernard357/plumbery.git
    $ cd plumbery
    $ python setup.py develop

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

Put secrets into local environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Run Plumbery from the command line
----------------------------------

As exposed before, plumbery can be run directly from the command line.
Move first to the directory that contains your fittings plan, and then run:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml build

Plumbery will load ``fittings.yaml``, then build all blueprints there.

As you can expect, plumbery can be invoked through the entire life cycle of
your fittings:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml build
    $ python -m plumbery fittings.yaml start
    $ python -m plumbery fittings.yaml polish

    ... nodes are up and running here ...

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy

To apply a polisher just mention its name on the command line. For example,
if fittings plan has a blueprint for nodes running Docker, then you may
use following statements to bootstrap each node:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml build docker
    $ python -m plumbery fittings.yaml start docker
    $ python -m plumbery fittings.yaml rub docker

    ... Docker is up and running at multiple nodes ...

If you create a new polisher and put it in the directory ``plumbery\polishers``,
then it will become automatically available:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml my_special_stuff

To get some help, you can type:

.. sourcecode:: bash

    $ python -m plumbery -h


As a next step, you are encouraged to have a deep look at the various files
put in the ``demos`` directory. There is a sophisticated ``fittings.yaml`` file
that demonstrates most advanced features supported by Plumbery. Many python
snippets and scripts are provided as well.


Use Plumbery as a python library
--------------------------------

Since Plumbery is easy to load, you can use it interactively like in the
following example:

.. sourcecode:: python

    >>>from plumbery.engine import PlumberyEngine
    >>>PlumberyEngine('fittings.yaml').build_blueprint('beachhead control')
    ...

If you are writing some code using Plumbery as a library, you would import
the engine and use it, as with any other python module. For example:

.. sourcecode:: python

    from plumbery.engine import PlumberyEngine

    engine = PlumberyEngine('fittings.yaml')
    engine.build_blueprint('docker')
    engine.start_nodes('docker')
    engine.polish_blueprint('docker', 'rub')


To go deeper into the code itself, you could have a look at the documentation
extracted from the code, at :ref:`modindex` and :ref:`genindex`. And of course
the source code is available on-line, check the `Plumbery repository at GitHub`_.

.. _`available on PyPi`: https://pypi.python.org/pypi/plumbery
.. _`Plumbery package at PiPy`: https://pypi.python.org/pypi/plumbery
.. _`Plumbery repository at GitHub`: https://github.com/bernard357/plumbery
.. _`download the reference fittings plan`: https://raw.githubusercontent.com/bernard357/plumbery/master/demos/fittings.yaml


