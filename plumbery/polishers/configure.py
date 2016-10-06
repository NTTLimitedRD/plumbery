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

import time

from plumbery.polisher import PlumberyPolisher
from plumbery.nodes import PlumberyNodes
from plumbery.exception import ConfigurationError
from plumbery.polishers.memory import MemoryConfiguration
from plumbery.polishers.cpu import CpuConfiguration
from plumbery.polishers.monitoring import MonitoringConfiguration
from plumbery.polishers.disks import DisksConfiguration
from plumbery.polishers.backup import BackupConfiguration
from plumbery.polishers.windows import WindowsConfiguration
from plumbery.plogging import plogging


class ConfigurePolisher(PlumberyPolisher):
    """
    Configures various elements in fittings plan

    This polisher looks at each node in sequence, and adjust settings
    according to fittings plan. This is covering various features that
    can not be set during the creation of nodes, such as:
    - number of CPU
    - quantity of RAM
    - monitoring
    - network interfaces

    """

    configuration_props = (MonitoringConfiguration,
                           DisksConfiguration, BackupConfiguration,
                           WindowsConfiguration)

    def move_to(self, facility):
        """
        Moves to another API endpoint

        :param facility: access to local parameters and functions
        :type facility: :class:`plumbery.PlumberyFacility`


        """

        self.facility = facility
        self.region = facility.region
        self.nodes = PlumberyNodes(facility)

    def shine_container(self, container):
        """
        Configures a container

        :param container: the container to be polished
        :type container: :class:`plumbery.PlumberyInfrastructure`

        """

        plogging.info("Configuring blueprint '{}'".format(
            container.blueprint['target']))

        if container.network is None:
            plogging.error("- aborted - no network here")
            return

        self.container = container

        plogging.info("- waiting for nodes to be deployed")

        names = self.nodes.list_nodes(container.blueprint)
        for name in names:
            while True:
                node = self.nodes.get_node(name)
                if node is None:
                    plogging.error("- aborted - missing node '{}'".format(name))
                    return

                if node.extra['status'].action is None:
                    break

                if (node is not None
                        and node.extra['status'].failure_reason is not None):

                    plogging.error("- aborted - failed deployment "
                                 "of node '{}'".format(name))
                    return

                time.sleep(20)

        plogging.info("- nodes have been deployed")

        container._build_firewall_rules()

        container._build_balancer()

    def set_node_compute(self, node, cpu, memory):
        """
        Sets compute capability

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :param cpu: the cpu specification
        :type cpu: ``DimensionDataServerCpuSpecification``

        :param memory: the memory size, expressed in Giga bytes
        :type memory: ``int``

        """

        changed = False

        if cpu is not None and 'cpu' in node.extra:

            if int(cpu.cpu_count) != int(node.extra['cpu'].cpu_count):
                plogging.info("- changing to {} cpu".format(
                    cpu.cpu_count))
                changed = True

            if (int(cpu.cores_per_socket) !=
                    int(node.extra['cpu'].cores_per_socket)):

                plogging.info("- changing to {} core(s) per socket".format(
                    cpu.cores_per_socket))
                changed = True

            if cpu.performance != node.extra['cpu'].performance:
                plogging.info("- changing to '{}' cpu performance".format(
                    cpu.performance.lower()))
                changed = True

        if memory is not None and 'memoryMb' in node.extra:

            if memory != int(node.extra['memoryMb']/1024):
                plogging.info("- changing to {} GB memory".format(
                    memory))
                changed = True

        if not changed:
            plogging.debug("- no change in compute")
            return

        if self.engine.safeMode:
            plogging.info("- skipped - safe mode")
            return

        while True:
            try:
                self.region.ex_reconfigure_node(
                    node=node,
                    memory_gb=memory,
                    cpu_count=cpu.cpu_count,
                    cores_per_socket=cpu.cores_per_socket,
                    cpu_performance=cpu.performance)

                plogging.info("- in progress")

            except Exception as feedback:
                if 'RESOURCE_BUSY' in str(feedback):
                    time.sleep(10)
                    continue

                if 'Please try again later' in str(feedback):
                    time.sleep(10)
                    continue

                plogging.info("- unable to reconfigure node")
                plogging.error(str(feedback))

            break

    def attach_node(self, node, networks):
        """
        Glues a node to multiple networks

        :param node: the target node
        :type node: :class:`libcloud.compute.base.Node`

        :param networks: a list of networks to connect, and ``internet``
        :type networks: list of ``str``

        This function adds network interfaces to a node, or adds address
        translation to the public Internet.

        Example in the fittings plan::

          - web:
              domain:
                ipv4: 6
              ethernet:
                name: gigafox.data
              nodes:
                - web[10..12]:
                    glue:
                      - gigafox.control
                      - internet 80 443

        In this example, another network interface is added to each node for
        connection to the Ethernet network ``gigafox.control``.

        Also, public IPv4 addresses are mapped on private addresses, so that
        each node web10, web11 and web12 is reachable from the internet.
        Public IPv4 addresses are taken from pool declared at the domain level,
        with the attribute ``ipv4``. In the example above, 6 addresses are
        assigned to the network domain, of which 3 are given to web nodes.

        If one or multiple numbers are mentioned after the keyword `internet`,
        they are used to configure the firewall appropriately.

        """

        hasChanged = False

        if node is None:
            return hasChanged

        for line in networks:

            tokens = line.strip(' ').split(' ')
            token = tokens.pop(0)

            if token.lower() == 'internet':
                self.attach_node_to_internet(node, tokens)
                continue

            if token == self.container.blueprint['ethernet']['name']:
                continue

            if token.lower() == 'primary':
                continue

            plogging.info("Glueing node '{}' to network '{}'"
                         .format(node.name, token))
            vlan = self.container.get_ethernet(token.split('::'))
            if vlan is None:
                plogging.info("- network '{}' is unknown".format(token))
                continue

            kwargs = {}
            if len(tokens) > 0:

                numbers = tokens.pop(0).strip('.').split('.')
                subnet = vlan.private_ipv4_range_address.split('.')
                while len(numbers) < 4:
                    numbers.insert(0, subnet[3-len(numbers)])

                private_ipv4 = '.'.join(numbers)
                plogging.debug("- using address '{}'".format(private_ipv4))
                kwargs['private_ipv4'] = private_ipv4

            if self.engine.safeMode:
                plogging.info("- skipped - safe mode")
                continue

            if 'private_ipv4' not in kwargs:
                kwargs['vlan'] = vlan

            while True:
                try:
                    self.region.ex_attach_node_to_vlan(node, **kwargs)
                    plogging.info("- in progress")
                    hasChanged = True

                except Exception as feedback:

                    if 'RESOURCE_BUSY' in str(feedback):
                        time.sleep(10)
                        continue

                    elif 'RESOURCE_LOCKED' in str(feedback):
                        plogging.info("- not now - locked")

                    elif 'INVALID_INPUT_DATA' in str(feedback):
                        plogging.info("- already there")

                    else:
                        plogging.info("- unable to glue node")
                        plogging.error(str(feedback))

                break

        return hasChanged

    def attach_node_to_internet(self, node, ports=[]):
        """
        Adds address translation for one node

        :param node: node that has to be reachable from the internet
        :type node: :class:`libcloud.common.Node`

        :param ports: the ports that have to be opened
        :type ports: a list of ``str``

        """

        plogging.info("Making node '{}' reachable from the internet"
                     .format(node.name))

        domain = self.container.get_network_domain(
            self.container.blueprint['domain']['name'])

        internal_ip = node.private_ips[0]

        external_ip = None
        for rule in self.region.ex_list_nat_rules(domain):
            if rule.internal_ip == internal_ip:
                external_ip = rule.external_ip
                plogging.info("- node is reachable at '{}'".format(external_ip))

        if self.engine.safeMode:
            plogging.info("- skipped - safe mode")
            return

        if external_ip is None:
            external_ip = self.container._get_ipv4()

            if external_ip is None:
                plogging.info("- no more ipv4 address available -- assign more")
                return

            while True:
                try:
                    self.region.ex_create_nat_rule(
                        domain,
                        internal_ip,
                        external_ip)
                    plogging.info("- node is reachable at '{}'".format(
                        external_ip))

                except Exception as feedback:
                    if 'RESOURCE_BUSY' in str(feedback):
                        time.sleep(10)
                        continue

                    elif 'RESOURCE_LOCKED' in str(feedback):
                        plogging.info("- not now - locked")
                        return

                    else:
                        plogging.info("- unable to add address translation")
                        plogging.error(str(feedback))

                break

        candidates = self.container._list_candidate_firewall_rules(node, ports)

        for rule in self.container._list_firewall_rules():

            if rule.name in candidates.keys():
                plogging.info("Creating firewall rule '{}'"
                             .format(rule.name))
                plogging.info("- already there")
                candidates = {k: candidates[k]
                              for k in candidates if k != rule.name}

        for name, rule in candidates.items():

            plogging.info("Creating firewall rule '{}'"
                         .format(name))

            if self.engine.safeMode:
                plogging.info("- skipped - safe mode")

            else:

                try:

                    self.container._ex_create_firewall_rule(
                        network_domain=domain,
                        rule=rule,
                        position='LAST')

                    plogging.info("- in progress")

                except Exception as feedback:

                    if 'NAME_NOT_UNIQUE' in str(feedback):
                        plogging.info("- already there")

                    else:
                        plogging.info("- unable to create firewall rule")
                        plogging.error(str(feedback))

    def shine_node(self, node, settings, container):
        """
        Finalizes setup of one node

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :param settings: the fittings plan for this node
        :type settings: ``dict``

        :param container: the container of this node
        :type container: :class:`plumbery.PlumberyInfrastructure`

        """

        plogging.info("Configuring node '{}'".format(settings['name']))
        if node is None:
            plogging.info("- not found")
            return

        try:
            cpu_prop = CpuConfiguration()
            cpu_prop.validate(settings)
            cpu = cpu_prop.configure(node, settings)

            ram_prop = MemoryConfiguration()
            ram_prop.validate(settings)
            memory = ram_prop.configure(node, settings)

            if memory is not False and cpu is not False:
                self.set_node_compute(node, cpu, memory)

        except ConfigurationError as ce:

            if self.engine.safeMode:
                plogging.warn(ce.message)
            else:
                raise ce

        for prop_cls in self.configuration_props:

            try:
                configuration_prop = prop_cls(engine=container.facility.plumbery,
                                              facility=self.facility)
                configuration_prop.validate(settings)
                configuration_prop.configure(node, settings)

            except ConfigurationError as ce:
                if self.engine.safeMode:
                    plogging.warn(ce.message)
                else:
                    raise ce

        if 'glue' in settings:
            self.attach_node(node, settings['glue'])

        container._add_to_pool(node)
