Selecting an image to deploy
============================

Each Cloud Server is linked to an image, like in the following exemple:

.. sourcecode:: yaml

    nodes:

      - myServer:

          appliance: 'Ubuntu 14'
          cpu: 2
          memory: 4

Selecting an image from the standard library
--------------------------------------------

Plumbery checks the standard library and looks for a matching image.
The lookup is based on strings, so they are multiple ways to use this.

====================================================  ===============================================================================
Example                                               Description
====================================================  ===============================================================================
``appliance: 'RedHat'``                               Pickup the first image with label 'RedHat' from the library
``appliance: 'RedHat 6 64-bit 2 CPU'``                Select the image with this exact name
``appliance: 'Ubuntu'``                               Select the most recent version of Ubuntu
``appliance: 'CentOS 5'``                             Select this exact version of CentOS
``appliance: 'Win2012 R2 DC'``                        Go for a version of Windows that is adapted to data centres
``appliance: 'Win2012 R2 Std'``                       Pickup a standard version on Windows operating system
``appliance: 'Check Point Security Gateway (BYOL)'``  Select an image from the Priced Software list
====================================================  ===============================================================================

Selecting an image from the client library
------------------------------------------

If no image can be found from the standard library, then plumbery looks into the client library.

====================================================  ===============================================================================
Example                                               Description
====================================================  ===============================================================================
``appliance: 'Web server with Chef client'``          Select a client image with this name
====================================================  ===============================================================================

