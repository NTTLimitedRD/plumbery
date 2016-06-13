Defining network domains
========================

Each blueprint can contain one domain configuration, like in the following exemple:

.. sourcecode:: yaml

    domain:
      description: "Demonstration of server orchestration at Dimension Data"
      name: MyDataCentre
      service: advanced
      ipv4: 2

Fitting attributes
------------------

=======================  ==========  ================================================================================================
Attribute                 Required    Description
=======================  ==========  ================================================================================================
name                      yes         Name of the network domain
description               no          Description of the network domain, that can include hashtags. No default
service                   no          Either **essentials** (default) or **advanced**
ipv4                      no          Quantity of public IPv4 addresses, or **auto**. Default is 0
=======================  ==========  ================================================================================================

The attribute ``ipv4:`` is used in conjunction with ``glue:``. See :doc:`fittings.glue` for more information on this topic.