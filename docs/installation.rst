============
Installation
============

At the prompt under Ubuntu 14.04:

    $ sudo apt-get install python-dev
    $ sudo pip install plumbery


Then put your secrets in  ``~/.bash_profile`` like this:

    # credentials to access cloud resources from Dimension Data
    export MCP_USERNAME=‘*** your account name here ***'
    export MCP_PASSWORD=’*** your password here ***'

    # password to access nodes remotely
    export SHARED_SECRET=’*** password to access nodes ***'

