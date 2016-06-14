Using from Docker
=================

The plumbery Docker image is the simplest and easiest way to use Plumbery, you can process multiple deployments at the same time, isolate the processes and there is no requirement to install any additional software. to download the plumbery image simply run:

.. sourcecode:: bash

    $ docker pull dimensiondataresearch/plumbery

This will download the latest image from https://hub.docker.com/r/dimensiondataresearch/plumbery/

You can then run the image with the following environment variables:

* **MCP_USERNAME** - your API username
* **MCP_PASSWORD** - your API password
* **SHARED_SECRET** - the password for the deployed servers
* **FITTINGS** - The URL to some fittings file, this can be a HTTP/HTTPS or a FTP/FTPS address. Look in https://github.com/DimensionDataCBUSydney/plumbery-contrib for examples

A fictitious example could be:

.. sourcecode:: bash

    $ docker run -e "MCP_USERNAME=bob_smith" -e "MCP_PASSWORD=superPassword!" \
         -e "SHARED_SECRET=superPassword!" \
         -e "FITTINGS=https://raw.githubusercontent.com/DimensionDataCBUSydney/plumbery-contrib/master/fittings/example/first/fittings.yaml" \
         dimensiondataresearch/plumbery

If needed, you have more variables to play with:

* **WGET_OPTS** can be set for the fetching of the fittings file, the following options are supported:
  * "--no-check-certificate" to disable SSL certificate validation
  * "--ftp-user=user --ftp-password=password" for FTP credentials
  * "--no-passive-ftp" disable FTP passive transfer mode, for use with proxys
  * "--http-user=user --http-password=password" for HTTP basic authentication
* **OPTS** can be set for the plumbery specific options, i.e.:
  * "-d" to set debug mode and get more information
  * "--safe" to only run the fittings file but not make any changes, for testing
* **ACTION** is "deploy" by default, but can be set to any of the potential actions for plumbery

