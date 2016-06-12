How to install plumbery?
========================

Adding plumbery as a new package on your workstation may be the simplest way to go.
Consider the installation from git if you want to get all of the source code.

.. toctree::
   :maxdepth: 1

   installing.plumbery.pip
   installing.plumbery.git


Configure a Linux machine, or a Mac
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default Plumbery reads credentials from the environment
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

Configure a Windows machine
~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default Plumbery reads credentials and other secrets from the environment
of the computer where it is running.

Download https://raw.githubusercontent.com/bagder/ca-bundle/master/ca-bundle.crt into %APPDATA%\libcloud

.. sourcecode:: powershell

    [Environment]::SetEnvironmentVariable("MCP_USERNAME", "myusername", "Process")
    [Environment]::SetEnvironmentVariable("MCP_PASSWORD", "mypassword!", "Process")
    [Environment]::SetEnvironmentVariable("SSL_CERT_FILE", "C:\Users\Anthony\AppData\Roaming\libcloud\ca-bundle.crt", "Process")


Test the installation
~~~~~~~~~~~~~~~~~~~~~

Ok, now you can check that plumbery can be triggered from the command line:

.. sourcecode:: bash

    $ python -m plumbery -v

This will display the version of the plumbery engine that is at your disposal.

Do a quick deployment
~~~~~~~~~~~~~~~~~~~~~

Open your preferred text editor to create a new file named ``fittings.yaml``.
Put the following content in it, save the file, and close the editor:

.. sourcecode:: bash

    locationId: EU6

    blueprints:

      - myBluePrint:
          domain:
            name: myDC
          ethernet:
            name: myVLAN
            subnet: 10.1.10.0
          nodes:
            - myServer:
                appliance: 'Ubuntu'

This is a very limited fittings file, yet it is all you need to deploy a new
server in the data centre of Frankfurt in Germany (Europe).

At this stage you are ready to deploy the fittings plan. The most straightforward command:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy

This will display a sequence of messages so that you can monitor what is done, and check that all steps are executed correctly.

If you hit an issue that you cannot explain, then make plumbery more verbose with the debug flag:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml deploy -d

In the end, keep in mind that resources deployed by plumbery are costing money to someone!
Hopefully, there is a simple way to stop the bill:

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml dispose

Congratulations! Plumbery has been installed and tested successfully!


.. _`available on PyPi`: https://pypi.python.org/pypi/plumbery
.. _`Plumbery package at PiPy`: https://pypi.python.org/pypi/plumbery
.. _`Plumbery repository at GitHub`: https://github.com/bernard357/plumbery
.. _`download the reference fittings plan`: https://raw.githubusercontent.com/bernard357/plumbery/master/demos/fittings.yaml


