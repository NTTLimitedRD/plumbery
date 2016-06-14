Configuring cloud backup
========================

Plumbery can orchestrate Cloud Backup, like in the following example:

.. sourcecode:: yaml


    nodes:

      - myServer:

          backup:
              plan: enterprise
              clients:
                  - type: file
                    schedulePolicy: 12AM - 6AM
                    storagePolicy: 14 Day Storage Policy
                  - type: mysql
                    schedulePolicy: 12AM - 6AM
                    storagePolicy: 14 Day Storage Policy
                    trigger: ON_SUCCESS_AND_FAILURE
                    email: me@me.com


