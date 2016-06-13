Selecting a data centre
=======================


.. code-block:: yaml
   :linenos:

    locationId: EU6
    regionId: dd-eu

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
domain acting as a virtual data centre, ``MyDataCentre``. Feel free to change
these to any values that would better suit you.

``locationId: EU6`` and ``regionId: dd-eu`` - The region defines the API
endpoint used by plumbery, and the location designates the target data centre
in the region. Look at the table below to select your preferred location.

  =======================  ============  ==========
  City                      locationId    regionId
  =======================  ============  ==========
  Amsterdam (Netherlands)       EU7        dd-eu
  Ashburn (US East)             NA9        dd-na
  Frankfurt (Germany)           EU6        dd-eu
  Hong Kong                     AP5        dd-ap
  London (UK)                   EU8        dd-eu
  Melbourne (Australia)        AU10        dd-au
  New-Zealand                  AU11        dd-au
  Santa Clara (US West)        NA12        dd-na
  Singapore                     AP3        dd-ap
  Sydney (Australia)            AU9        dd-au
  Tokyo (Japan)                 AP4        dd-ap
  =======================  ============  ==========

