Configuring CPU and memory
==========================

Plumbery has the ability to adjust CPU and RAM to exact configurations, like in the following example:

.. sourcecode:: yaml


    nodes:

      - myServer:

          appliance: 'Ubuntu 14'
          cpu: 16 2 highperformance
          memory: 48

Components of the ``cpu:`` directive
------------------------------------

=======================  ==========  ================================================================================================
Component                 Required    Description
=======================  ==========  ================================================================================================
number of CPU             yes         An integer between 1 and 32
number of core            no          Either 1 or 2. Default is 1.
class of CPU              no          Either ``standard`` (default) or ``highperformance``
=======================  ==========  ================================================================================================

The ``memory:`` directive
-------------------------

This is the quantity of RAM in GB, expressed as an integer between 1 and 256.


