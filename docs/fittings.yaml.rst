Fittings file are based on YAML
===============================

Multiple documents in one fittings file
---------------------------------------

YAML allows for multiple documents to be assembled in one fittings plan.
The separation of documents is done with three dashes at the beginning of a line.
The first document is reserved for plumbery parameters, default settings, etc.
Therefore the description of blueprints starts on the second document::

.. sourcecode:: yaml

    ---
    information:
      - "NFS client and server at two different data centres"

    ---
    blueprints:
      ...

Deploying in multiple geographies
---------------------------------

Since Plumbery processes each document independently, it is really easy to configure
a deployment that spans multiple data centres, like in the following example::

.. sourcecode:: yaml

    ---
    information:
      - "Multi-Geography deployment example"
    ---
    regionId: dd-eu
    locationId: EU6
    blueprints:
      ...
    ---
    regionId: dd-na
    locationId: NA9
    blueprints:
      ...

Combining private and public clouds in a deployment
---------------------------------------------------

Private MCPs are set using the apiHost parameter, you must also include the datacenter ID of the cloud as the locationId.
You can then include another document(s) with the public cloud fittings::

.. sourcecode:: yaml

    ---
    information:
      - "Multi-Geography deployment example"
    ---
    apiHost: my-private-cloud.com
    locationId: MY1
    blueprints:
      ...
    ---
    regionId: dd-na
    locationId: NA9
    blueprints:
      ...