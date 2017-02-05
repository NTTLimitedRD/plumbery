# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import yaml

from plumbery.action import PlumberyAction
from plumbery.plogging import plogging


class InventoryAction(PlumberyAction):
    """
    Captures inventory information

    :param settings: specific settings for this action
    :type param: ``dict``

    This action looks at each node in sequence, but only to retrieve
    maximum information about each of them. At the end of the process,
    a YAML file is written for future reference.

    To activate this action you have to mention it in the fittings plan,
    like in the following example::

        ---
        actions:
          - inventory:
              output: inventory.yaml
        ---
        # Frankfurt in Europe
        locationId: EU6
        regionId: dd-eu
        ...


    """

    def begin(self, engine):
        """
        Restarts the inventory process
        """

        super(InventoryAction, self).begin(engine)

        self.inventory = []

    def process(self, blueprint):
        plogging.info("- process blueprint")

    def end(self):
        """
        Saves information gathered through the polishing sequence

        All information captured in dumped in a file, in YAML format,
        to provide a flexible and accurate inventory of all live nodes
        described in the fittings plan.

        """

        if len(self.inventory) < 1:
            return

        fileName = self.get_parameter('output', None)
        if fileName:
            plogging.info("Writing inventory in '{}'".format(fileName))
            stream = open(fileName, 'w')
        else:
            plogging.info("Showing the inventory")
            stream = sys.stdout

        stream.write(yaml.dump(self.inventory, default_flow_style=False))
