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


class SpitPolisher(PlumberyPolisher):
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
              file: nodes.yaml
          - ansible:
              file: inventory.yaml
        ---
        # Frankfurt in Europe
        locationId: EU6
        regionId: dd-eu
        ...


    """

    def go(self):
        """
        Restarts the inventory process
        """

        self.inventory = []

    def shine_node(self, node, settings):
        """
        Gets as much information as possible from a node

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :param settings: the fittings plan for this node
        :type settings: ``dict``

        """

        self.inventory.append(self._spit(node))

    def _spit(self, node):
        """
        Puts node information in a flat dictionary

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :returns: ``dict`` - flatten attributes of the node

        Please note that the information returned is a combination of
        attributes exposed by Apache Libcloud and of extra fields
        provided by Dimension Data.

        """
        data = {}
        data['id'] = node.id
        data['name'] = node.name
        data['private_ip'] = node.private_ips[0]
        data.update(node.extra)
        data.pop('status')

        return data

    def reap(self):
        """
        Saves information gathered through the polishing sequence

        All information captured in dumped in a file, in YAML format,
        to provide a flexible and accurate inventory of all live nodes
        described in the fittings plan.

        """

        if 'file' in self.settings:
            fileName = self.settings['file']
        else:
            fileName = 'spit.yaml'

        logging.info("Spitting in '{}'".format(fileName))
        with open(fileName, 'w') as stream:
            stream.write(yaml.dump(self.inventory, default_flow_style=False))
            stream.close()
