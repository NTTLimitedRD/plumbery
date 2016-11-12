Installing plumbery on Microsoft Windows
========================================

The setup process on Microsoft Windows will take you about 15 minutes in total. At the end of the process, you will be in a position to control your infrastructure at any Managed Cloud Control (MCP) of Dimension Data. As a first step you will install python and related stuff, then plumbery itself, then you will configure your MCP credentials and test the full setup.

Install python 2.7
------------------

You will need the latest version of the Python 2.7 language, which you can download from
the following address::

    http://python.org/download/releases/2.7/

Paste this address in a web browser, download the appropriate package for your machine, and then run it.
For the most common case, which is likely the MSI 64 bits installer for Windows, you may want to use following shortcut::

    https://www.python.org/ftp/python/2.7/python-2.7.amd64.msi

The Windows version is provided as an MSI package. To install it manually, just double-click the file. The MSI package format allows Windows administrators to automate installation with their standard tools.

By design, Python installs to a directory with the version number embedded, e.g. Python version 2.7 will install at C:\Python27\, so that you can have multiple versions of Python on the same system without conflicts. Of course, only one interpreter can be the default application for Python file types.

At the end of the process, open a command shell and check the version of python like this::

    >cd C:\Python27
    >python -v

If the system complains that the directory does not exist, or that it can not find python, then something went wrong during the download or the installation steps.
On the other hand, if you get a proper version number, which is very likely, than you can exit the interpreter and move to the next step::

    >>>exit()
    >

Typing the full path name for a Python interpreter each time quickly gets tedious, so add the directories for your default Python version to the PATH. Assuming that your Python installation is in C:\Python27\, add this to your PATH::

    C:\Python27\;C:\Python27\Scripts\

The second directory receives command files when certain packages are installed, such as pip and others, so it is a very useful addition.

You can do this by running the following in powershell::

    [Environment]::SetEnvironmentVariable("Path", "$env:Path;C:\Python27\;C:\Python27\Scripts\", "User")

Alternatively, open the Configuration Panel and look for System settings. Then append the following to the system environment variable PATH and save your change::

    C:\Python27\;C:\Python27\Scripts\


Install pip with get-pip.py
---------------------------

Pip is a manager of python packages. We will use it to install various packages that are useful to plumbery, such as Apache Libcloud and others.

Paste the following address in a browser window and save the file locally::

    https://bootstrap.pypa.io/get-pip.py

Then in a command shell, ask python to run the downloaded file::

    >python <where_file_has_been_downloaded>\get-pip.py

After the installation of pip you can get a full list of packages that have been installed on your workstation::

    >pip freeze

Install Microsoft Visual C++ Compiler for Python 2.7
----------------------------------------------------

Because some low-level software require local compilation, you will install the Microsoft Visual C++ Compiler for Python 2.7 from following address::

    https://www.microsoft.com/en-us/download/confirmation.aspx?id=44266

This will provide you with a MSI file that you have to download and execute on your workstation, like you did for python itself.


Install apache-libcloud
-----------------------

Now that building blocks have put together, we will pull Apache Libcloud and install it locally.
Go the directory where pip executable has been put, and ask it to install Apache Libcloud::

    >pip install apache-libcloud


Install ca-bundles.cert
-----------------------

Since plumbery interacts with virtual servers over SSH, it relies on some certificates that have to be installed locally.
As usual with information security, this could be really painful and complicated.
But hopefully some smart guys have bundled common certificates into a single file, that will make our life easier.

Download the bundle from following link:

    https://raw.githubusercontent.com/bagder/ca-bundle/master/ca-bundle.crt

Save the file on local disk, then double-click on it. Microsoft Windows will check your intention. Confirm that you want to add the certificates to your system.

Alternatively, you can achieve the same result from PowerShell:

.. sourcecode:: powershell

    [Environment]::SetEnvironmentVariable("SSL_CERT_FILE", "<location of download of the ca-bundle.crt file>", "Process")

Install plumbery
----------------

Plumbery is a regular python package that has been made `available on PyPi`_.
So it is a no-brainer to install it with pip::

    >pip install virtualenv
    >virtualenv.exe .
    >pip install plumbery

Test your installation
----------------------

The following command loads plumbery and ask it to display its version number::

    >python -m plumbery -v


Set run-time environment variables
----------------------------------

By default Plumbery reads credentials and other secrets from the environment
of the computer where it is running.

Following system variables are expected by plumbery:

* MCP_USERNAME - This is the user name that you use to connect to CloudControl

* MCP_PASSWORD - This is the password that you enter in CloudControl

* SHARED_SECRET - This is the admin/root password that is communicated to new servers created over the API.
You should select a long and difficult pass phrase.

You can do this by running the following in powershell::

.. sourcecode:: powershell

    [Environment]::SetEnvironmentVariable("MCP_USERNAME", "<your user name here>", "Process")
    [Environment]::SetEnvironmentVariable("MCP_PASSWORD", "<your password here>", "Process")
    [Environment]::SetEnvironmentVariable("SHARED_SECRET", "<a long and difficult pass phrase here>", "Process")

Alternatively, open the Configuration Panel and look for System settings. Then add system environment variables
MCP_USERNAME, MCP_PASSWORD and SHARED_SECRET and save your changes.


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
          nodes:
            - myServer:
                appliance: 'Ubuntu'

This is a very limited configuration file, yet it is all you need to deploy a new
server in the data centre of Frankfurt in Germany (Europe).

At this stage you are ready to deploy the configuration file. The most straightforward command::

    >python -m plumbery fittings.yaml deploy

This will display a sequence of messages so that you can monitor what is done, and check that all steps are executed correctly.

If plumbery complains about some missing variable, then close all command shells and re-open a new one so that it gets updated environment variables.

If you hit an issue that you cannot explain, then make plumbery more verbose with the debug flag::

    >python -m plumbery fittings.yaml deploy -d

In the end, keep in mind that resources deployed by plumbery are costing money to someone!
Hopefully, there is a simple way to stop the bill::

    >python -m plumbery fittings.yaml dispose

Congratulations! Plumbery has been installed and tested successfully!



.. _`available on PyPi`: https://pypi.python.org/pypi/plumbery
.. _`Plumbery package at PiPy`: https://pypi.python.org/pypi/plumbery


