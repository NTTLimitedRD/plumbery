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

from plumbery.polishers.inventory import InventoryPolisher
from plumbery.plogging import plogging


class AnsiblePolisher(InventoryPolisher):
    """
    Captures inventory information for ansible

    This polisher looks at each node in sequence, but only to retrieve
    maximum information about each of them. At the end of the process,
    the polisher writes a YAML file to feed ansible.

    To activate this polisher you have to mention it in the fittings plan,
    like in the following example::

        ---
        safeMode: False
        polishers:
          - ansible:
              reap: inventory.yaml
        ---
        # Frankfurt in Europe
        locationId: EU6
        regionId: dd-eu
        ...


    """

    def reap(self):
        """
        Saves information gathered through the polishing sequence

        All information captured in dumped in a file, in YAML format,
        to provide a flexible and accurate inventory of live nodes
        that are part of the fittings plan.

        The private ipv4 network addresses are attached to each host, so that
        ansible do not need to rely on DNS settings.

        Plumbery also provides multiple groups of hosts to ansible, based on
        various criteria:

        * data center location
        * hashtags in node description

        As an example, let consider the following fittings plan::

            ---
            locationId: EU6
            regionId: dd-eu
            blueprints:
              - sql:
                  domain: *vdc1
                  ethernet: *data
                  nodes:
                    - slaveSQL:
                        description: 'SQL #vdc1 #secondary'
                        appliance: 'RedHat 6 64-bit 4 CPU'
            ---
            locationId: EU7
            regionId: dd-eu
            blueprints:
              - sql:
                  domain: *vdc2
                  ethernet: *data
                  nodes:
                    - masterSQL:
                        description: 'SQL #vdc2 #primary'
                        appliance: 'RedHat 6 64-bit 4 CPU'


        After the creation of nodes by plumbery, the inventory provided to
        ansible could look like this::

            masterSQL ansible_host=10.2.3.8
            slaveSQL ansible_host=10.1.3.8

            [EU6]
            slaveSQL

            [EU7]
            masterSQL

            [plumbery]
            masterSQL
            slaveSQL

            [primary]
            masterSQL

            [secondary]
            slaveSQL

            [vdc1]
            slaveSQL

            [vdc2]
            masterSQL


        Ok, with two nodes it may be quite difficult to find excitment in
        a sophisticated inventory, but you get the idea.

        """

        hosts = []
        groups = {}

        for item in self.inventory:
            host = item['name']

            if len(item['public_ips']) > 0:
                host_address = item['public_ips'][0]
            elif item['ipv6']:
                host_address = item['ipv6']
            else:
                host_address = item['private_ips'][0]

            hosts.append("{} private_ipv4={} ansible_ssh_host={}".format(
                host, host_address, host_address))

            group = item['datacenterId']
            if group not in groups.keys():
                groups[group] = []
            groups[group].append(host)

            description = item['description']
            tags = {tag.strip("#") for tag in description.split()
                    if tag.startswith("#")}
            for tag in tags:
                if tag not in groups.keys():
                    groups[tag] = []
                groups[tag].append(host)

        if 'reap' in self.settings:
            fileName = self.settings['reap']
            plogging.info("Writing inventory for ansible in '{}'".format(
                fileName))
            stream = open(fileName, 'w')
        else:
            plogging.info("Showing the inventory for ansible")
            stream = sys.stdout

        for line in sorted(hosts):
            stream.write(line+'\n')
        stream.write('\n')

        for group in sorted(groups.keys()):
            stream.write('[{}]\n'.format(group))
            for host in sorted(groups[group]):
                stream.write('{}\n'.format(host))
            stream.write('\n')
        stream.write('\n')
