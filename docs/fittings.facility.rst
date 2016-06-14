Selecting a data centre
=======================


.. code-block:: yaml
   :linenos:

    regionId: dd-eu
    locationId: EU6

    blueprints:

      - myBluePrint:
          domain:
            name: myDC
          ethernet:
            name: myVLAN
            subnet: 10.1.10.0
          nodes:
            - myServer

In this example the server ``MyServer`` is placed in a
network named ``MyNetwork``, and the network is part of a network
domain acting as a virtual data centre, ``MyDataCentre``.

The overarching location of these resources is defined by ``locationId: EU6`` and ``regionId: dd-eu``.

How to select a public data centre?
-----------------------------------

The directive ``regionId:`` defines the API endpoint used by plumbery, while
``locationId:`` selects a data centre in the region.

The table below provides a table of public data centres that are available
with this approach.

===========================  ==========  ===============  ==========
City                         locationId  Region           regionId
===========================  ==========  ===============  ==========
Amsterdam (Netherlands)      EU7         Europe           dd-eu
Ashburn (US East)            NA9         United States    dd-na
Frankfurt (Germany)          EU6         Europe           dd-eu
Hong Kong                    AP5         Asia-Pacific     dd-ap
Johannesburg (South Africa)  AF3         Africa           dd-af
London (UK)                  EU8         Europe           dd-eu
Melbourne (Australia)        AU10        Australia        dd-au
New-Zealand                  AU11        Australia        dd-au
Santa Clara (US West)        NA12        North America    dd-na
Singapore                    AP3         Asia-Pacific     dd-ap
Sydney (Australia)           AU9         Australia        dd-au
Tokyo (Japan)                AP4         Asia-Pacific     dd-ap
Toronto                      CA2         Canada           dd-ca
===========================  ==========  ===============  ==========

In simplest cases, plumbery can deduce the region from the location. In other terms,
if you mention ``locationId`` then you may drop the ``regionId`` directive.

For example:

.. sourcecode:: yaml

    locationId: EU6

    blueprints:
      ...


How to select a private data centre?
------------------------------------

Private data centres installed by Dimension Data have their own API endpoint.
To drive plumbery to the right place you can use the directive ``apiHost:`` and
then designate the data centre with ``locationId:``.

For example:

.. sourcecode:: yaml

    ---
    information:
      - "Private deployment example"
    ---
    apiHost: my-private-cloud.com
    locationId: MY1
    blueprints:
      ...

