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
  name                      yes         A name for the network domain
  description               no          A description of the network domain, that can include hashtags. No default
  service                   no          Either **essentials** (default) or **advanced**
  ipv4                      no          The maximum number of public IPv4 addresses to consume in the domain, or **auto**. Default is 0
  =======================  ==========  ================================================================================================
