Installing plumbery package
===========================

You will need the latest version of the Python 2.7 language, which you can download for Linux, Mac and Windows at
the following address::

  http://python.org/download/releases/2.7/

You need pip, a package management system, to install modules related to plumbery.
Should your Linux system not have pip installed, run this command:

.. sourcecode:: bash

    $ sudo apt-get install python-pip

For Windows users: look in folder `C:\Python27\Scripts` after the installation of Python 2.7, this is where
the pip executable has been put.

Install Apache Libcloud
-----------------------

The orchestration of cloud services is a hot topic these days. Apache Libcloud may be among the most popular
solutions based on python. This is the one that we have selected for plumbery:

On Linux or on Mac OSX:

.. sourcecode:: bash

    $ sudo pip install apache-libcloud

On Windows:

.. sourcecode:: powershell

    > pip install apache-libcloud


Install the plumbery package
----------------------------

Plumbery is available as a python package, so the installation, the upgrade,
and the removal of the software are really easy.

Install the plumbery package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plumbery is `available on PyPi`_. You can install latest stable version using pip.

On Linux or on Mac OSX:

.. sourcecode:: bash

    $ sudo apt-get install python-pip python-dev
    $ sudo pip install plumbery

The installation of `python-dev` is required for the installation of the module
`netifaces`, that is used by Plumbery to get information about network interfaces.

On Windows:

For installation on Windows, you may need to first install the Python Compiler for VC++. https://www.microsoft.com/en-us/download/confirmation.aspx?id=44266
Note this only works for Python 2.7. If you get an error on installation saying "error: Unable to find vcvarsall.bat" this indicates you need to install this package.

.. sourcecode:: powershell

    > pip install virtualenv
    > virtualenv.exe .
    > .\Script\pip install plumbery

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

.. _`available on PyPi`: https://pypi.python.org/pypi/plumbery
.. _`Plumbery package at PiPy`: https://pypi.python.org/pypi/plumbery


