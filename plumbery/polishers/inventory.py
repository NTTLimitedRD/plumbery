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

from plumbery.polisher import PlumberyPolisher
from plumbery.plogging import plogging


class InventoryPolisher(PlumberyPolisher):
    """
    Captures inventory information

    This polisher looks at each node in sequence, but only to retrieve
    maximum information about each of them. At the end of the process,
    the polisher writes a YAML file for future reference.

    To activate this polisher you have to mention it in the fittings plan,
    like in the following example::

        ---
        polishers:
          - inventory:
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

        super(InventoryPolisher, self).go(engine)

        self.inventory = []

    def shine_node(self, node, settings, container):
        """
        Gets as much information as possible from a node

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :param settings: the fittings plan for this node
        :type settings: ``dict``

        :param container: the container of this node
        :type container: :class:`plumbery.PlumberyInfrastructure`

        Please note that the information saved here is a combination of
        attributes exposed by Apache Libcloud and of extra fields
        provided by Dimension Data.

        """

        plogging.info("Examinating node '{}'".format(settings['name']))
        if node is None:
            plogging.info("- not found")
            return

        data = {}
        data['type'] = 'node'
        data['id'] = node.id
        data['name'] = node.name

        data['state'] = node.state

        status = None
        if 'status' in node.extra:
            status = node.extra.pop('status')
            data['action'] = str(status.action)

        if 'cpu' in node.extra:
            cpu = node.extra.pop('cpu')
            data['cpu'] = cpu.cpu_count
            data['cpuCoresPerSocket'] = cpu.cores_per_socket
            data['cpuPerformance'] = cpu.performance.lower()

        if 'memoryMb' in node.extra:
            memory = node.extra.pop('memoryMb')
            data['memory'] = int(memory/1024)

        if 'networkId' in node.extra:
            node.extra.pop('networkId')

        data.update(node.extra)

        domain = container.get_network_domain(
            container.blueprint['domain']['name'])

        if domain is not None:
            data['datacenter'] = domain.location.name
            data['datacenterCountry'] = domain.location.country
            data['networkDomain'] = domain.name
            data['networkDomainDescription'] = domain.description

        ethernet = container.get_ethernet(
            container.blueprint['ethernet']['name'])

        if ethernet is not None:
            data['ethernet'] = ethernet.name
            data['ethernetId'] = ethernet.id
            data['ethernetDescription'] = ethernet.description

        data['public_ips'] = node.public_ips
        data['private_ips'] = node.private_ips

        data['private_host'] = node.private_ips[0].replace('.', '-')

        tags = []
        tags.append("state_{}".format(data['state']))
        tags.append("location_{}".format(data['datacenterId']))
        if 'networkDomain' in data:
            tags.append("domain_{}".format(data['networkDomain']))
        if 'ethernet' in data:
            tags.append("network_{}".format(data['ethernet']))
        description = node.extra['description'].replace(
            '#plumbery', '').strip()
        tags += {tag.strip("#") for tag in description.split()
                 if tag.startswith("#")}
        data['tags'] = tags

        self.inventory.append(data)

        plogging.info("- done")

    def reap(self):
        """
        Saves information gathered through the polishing sequence

        All information captured in dumped in a file, in YAML format,
        to provide a flexible and accurate inventory of all live nodes
        described in the fittings plan.

        """

        if len(self.inventory) < 1:
            return

        if 'reap' in self.settings:
            fileName = self.settings['reap']
            plogging.info("Writing inventory in '{}'".format(fileName))
            stream = open(fileName, 'w')
        else:
            plogging.info("Showing the inventory")
            stream = sys.stdout

        stream.write(yaml.dump(self.inventory, default_flow_style=False))
