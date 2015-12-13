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

import logging
import yaml

from plumbery.polisher import PlumberyPolisher


class InventoryPolisher(PlumberyPolisher):
    """
    Captures inventory information

    This polisher looks at each node in sequence, but only to retrieve
    maximum information about each of them. At the end of the process,
    the polisher writes a YAML file for future reference.

    To activate this polisher you have to mention it in the fittings plan,
    like in the following example::

        ---
        safeMode: False
        polishers:
          - spit:
              reap: nodes.yaml
          - ansible:
              reap: inventory.yaml
        ---
        # Frankfurt in Europe
        locationId: EU6
        regionId: dd-eu
        ...


    """

    def go(self, engine):
        """
        Restarts the inventory process
        """

        self.engine = engine

        self.inventory = []

    def shine_node(self, node, settings):
        """
        Gets as much information as possible from a node

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :param settings: the fittings plan for this node
        :type settings: ``dict``

        Please note that the information saved here is a combination of
        attributes exposed by Apache Libcloud and of extra fields
        provided by Dimension Data.

        """

        data = {}
        data['type'] = 'node'
        data['id'] = node.id
        data['name'] = node.name
        data['public_ips'] = node.public_ips
        data['private_ips'] = node.private_ips
        data.update(node.extra)
        data.pop('status')

        self.inventory.append(data)

    def reap(self):
        """
        Saves information gathered through the polishing sequence

        All information captured in dumped in a file, in YAML format,
        to provide a flexible and accurate inventory of all live nodes
        described in the fittings plan.

        """

        if 'reap' in self.settings:
            fileName = self.settings['reap']
        else:
            fileName = 'inventory.yaml'

        logging.info("Writing inventory in '{}'".format(fileName))
        with open(fileName, 'w') as stream:
            stream.write(yaml.dump(self.inventory, default_flow_style=False))
            stream.close()
