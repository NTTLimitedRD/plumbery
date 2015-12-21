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
import re
import time

try:
    from lxml import etree as ET
except ImportError:
    from xml.etree import ElementTree as ET

from libcloud.compute.base import NodeAuthPassword
from libcloud.compute.base import NodeState
from libcloud.utils.xml import fixxpath, findtext, findall
from libcloud.common.dimensiondata import TYPES_URN
#from libcloud.common.dimensiondata import DimensionDataServerCpuSpecification

from domain import PlumberyDomain
from exceptions import PlumberyException

__all__ = ['PlumberyNodes']


class PlumberyNodes:
    """
    Cloud automation for computing nodes

    :param facility: the underlying physical facility
    :type facility: :class:`plumbery.PlumberFacility`

    A node is a virtual machine with some permanent storage, and one or several
    network connections. It can have many attributes, such as the number of
    CPU, some memory, an operating system, etc.

    Example::

        from plumbery.nodes import PlumberyNodes
        nodes = PlumberyNodes(facility)
        nodes.build_blueprint(blueprint, container)

    In this example an instance is initialised at the given facility, and then
    it is asked to create nodes described in the provided blueprint.
    This is not covering network and the security, but only the nodes.

    Attributes:
        facility (PlumberyFacility):
            a handle to the physical facility where nodes are deployed
            are implemented

    """

    plumbery = None

    def __init__(self, facility=None):
        """Put nodes in context"""

        # handle to parent parameters and functions
        self.facility = facility
        self.region = facility.region
        self.plumbery = facility.plumbery

    def __repr__(self):

        return "<PlumberyNodes facility: {}>".format(self.facility)

    def build_blueprint(self, blueprint, container):
        """
        Create missing nodes

        :param blueprint: the blueprint to build
        :type blueprint: ``dict``

        :param container: the container where nodes will be built
        :type container: :class:`plumbery.PlumberyDomain`

        """

        self.facility.power_on()

        if 'nodes' not in blueprint or not isinstance(blueprint['nodes'], list):
            logging.info("No nodes have been defined")
            return

        for item in blueprint['nodes']:

            if type(item) is dict:
                label = item.keys()[0]
                settings = item.values()[0]

            else:
                label = item
                settings = {}

            for label in self.expand_labels(label):

                if self.get_node(label):
                    logging.info("Creating node '{}'".format(label))
                    logging.info("- already done")
                    continue

                description = '#plumbery'
                if 'description' in settings:
                    description = settings['description'] + ' #plumbery'

                if 'appliance' in settings:
                    imageName = settings['appliance']
                else:
                    imageName = 'Ubuntu'

#                if 'cpu' in settings:
#                    tokens = settings['cpu'].split(' ')
#                    if len(tokens) < 3:
#                        tokens.append('1')
#                        tokens.append('STANDARD')
#
#                    cpu = DimensionDataServerCpuSpecification(
#                                        cpu_count=tokens[0],
#                                        cores_per_socket=tokens[1],
#                                        performance=tokens[2])
#                else:
#                    cpu = None

                if 'memory' in settings:
                    memory = settings['memory']
                else:
                    memory = None

                image = self.facility.get_image(imageName)
                if image is None:
                    raise PlumberyException("Error: unable to find image "
                                                "for '{}'!".format(imageName))

                if self.plumbery.safeMode:
                    logging.info("Would have created node '{}' "
                                    "if not in safe mode".format(label))
                    continue

                logging.info("Creating node '{}'".format(label))

                if not container.domain:
                    logging.info("- missing network domain")
                    continue
                if not container.network:
                    logging.info("- missing Ethernet network")
                    continue

                while True:

                    try:
                        self.region.create_node(
                            name=label,
                            image=image,
                            auth=NodeAuthPassword(
                                self.plumbery.get_shared_secret()),
                            ex_network_domain=container.domain,
                            ex_vlan=container.network,
#                            ex_cpu_specification=cpu,
#                            ex_memory_gb=memory,
                            ex_is_started=False,
                            ex_description=description)
                        logging.info("- in progress")

                    except Exception as feedback:

                        if 'RESOURCE_BUSY' in str(feedback):
                            time.sleep(10)
                            continue

                        elif 'RESOURCE_NOT_FOUND' in str(feedback):
                            logging.info("- not now")
                            logging.info(str(feedback))

                        elif 'RESOURCE_LOCKED' in str(feedback):
                            logging.info("- not now - locked")
                            logging.info(str(feedback))

                        else:
                            logging.info("- unable to create node")
                            logging.info(str(feedback))

                    break

    def destroy_blueprint(self, blueprint):
        """
        Destroys nodes of a given blueprint

        :param blueprint: the blueprint to build
        :type blueprint: ``dict``

        """

        self.facility.power_on()

        domains = PlumberyDomain(self.facility)
        container = domains.get_container(blueprint)

        if 'nodes' not in blueprint or not isinstance(blueprint['nodes'], list):
            return

        # destroy in reverse order
        for item in reversed(blueprint['nodes']):

            if type(item) is dict:
                label = item.keys()[0]
                settings = item[label]
            else:
                label = str(item)
                settings = {}

            for label in self.expand_labels(label):

                if self.plumbery.safeMode:
                    logging.info("Would have destroyed node '{}' "
                                    "if not in safe mode".format(label))
                    continue

                node = self.get_node(label)
                if node is None:
                    logging.info("Destroying node '{}'".format(label))
                    logging.info("- not found")
                    continue

                if 'destroy' in settings and settings['destroy'] == 'never':
                    logging.info("Destroying node '{}'".format(label))
                    logging.info("- this node can never be destroyed")
                    return False

                if node.state == NodeState.RUNNING:
                    logging.info("Destroying node '{}'".format(label))
                    logging.info("- skipped - node is up and running")
                    continue

                self._stop_monitoring(node, settings)
                self._detach_node(node, settings)
                container._detach_node_from_internet(node)
                container._remove_from_balancer(node)

                logging.info("Destroying node '{}'".format(label))
                while True:

                    try:
                        self.region.destroy_node(node)
                        logging.info("- in progress")

                    except Exception as feedback:

                        if 'RESOURCE_BUSY' in str(feedback):
                            time.sleep(10)
                            continue

                        elif 'RESOURCE_NOT_FOUND' in str(feedback):
                            logging.info("- not found")

                        elif 'SERVER_STARTED' in str(feedback):
                            logging.info("- skipped - node is up and running")

                        elif 'RESOURCE_LOCKED' in str(feedback):
                            logging.info("- not now - locked")
                            return False

                        else:
                            logging.info("- unable to destroy node")
                            logging.info(str(feedback))

                    break

    def _detach_node(self, node, settings):
        """
        Detach a node from multiple networks

        :param node: the target node
        :type node: :class:`libcloud.compute.base.Node`

        This function removes all secondary network interfaces to a node, and
        any potential translation to the public Internet.

        """

        if node is None:
            return True

        if 'running' in settings and settings['running'] == 'always':
            return True

        for interface in self._list_secondary_interfaces(node):

            logging.info("Detaching node '{}' from network '{}'"
                                      .format(node.name, interface['network']))

            while True:
                try:
                    self.region.ex_destroy_nic(interface['id'])
                    logging.info("- in progress")

                except Exception as feedback:

                    if 'RESOURCE_BUSY' in str(feedback):
                        time.sleep(10)
                        continue

                    elif 'RESOURCE_LOCKED' in str(feedback):
                        logging.info("- not now - locked")

                    elif 'NO_CHANGE' in str(feedback):
                        logging.info("- already done")

                    else:
                        logging.info("- unable to detach node")
                        logging.info(str(feedback))
                        return False

                break

        return True

    @classmethod
    def expand_labels(self, label):
        """
        Designate multiple nodes with a simple label

        :param label: the label to be expanded, e.g., ``server[1..2]_eu``
        :type label: ``str``

        :return: a list of labels, e.g., ``['server1_eu', 'server2_eu']``
        :rtype: ``list`` of ``str``

        This function creates multiple names where applicable::

            >>>nodes.expand_labels('mongodb')
            ['mongodb']
            >>>nodes.expand_labels('mongodb[1..3]_eu')
            ['mongodb1_eu', 'mongodb2_eu', 'mongodb3_eu']

        """
        matches = re.match(r'(.*)\[([0-9]+)..([0-9]+)\](.*)', label)
        if matches is None:
            return [label]

        labels = []
        for index in range(int(matches.group(2)), int(matches.group(3))+1):
            labels.append(matches.group(1)+str(index)+matches.group(4))
        return labels

    def get_node(self, name):
        """
        Retrieves a node by name

        :param name: the name of the target node
        :type name: ``str``

        :return: the target node, or None
        :rtype: :class:`libcloud.compute.base.Node`

        This function always make a real API call to get fresh state of the
        target node. Therefore, it can be used in loops where you monitor
        the evolution of the node during build or other change operation.

        """

        self.facility.power_on()

        node = None
        for node in self.region.list_nodes():

            # skip nodes from other locations
            if node.extra['datacenterId'] != self.facility.get_location_id():
                continue

#           # skip nodes from other network domains
#           if node.extra['networkDomainId'] != self.domain.id:
#               continue

            # found a node with this name
            if node.name == name:
                self._update_ipv6(node)
                return node

        return None

    @classmethod
    def list_nodes(self, blueprint):
        """
        Retrieves the list of nodes that have been defined for this blueprint.

        :return: names of nodes defined for this blueprint
        :rtype: ``list`` of ``str`` or []

        """

        labels = set()
        if 'nodes' in blueprint:
            for item in blueprint['nodes']:
                if type(item) is dict:
                    label = item.keys()[0]
                    settings = item.values()[0]

                else:
                    label = item
                    settings = {}

                for label in PlumberyNodes.expand_labels(label):
                    labels.add(label)

        return list(labels)

    def _list_secondary_interfaces(self, node):
        """
        Retrieves the list of secondary interfaces

        This is a hack. Code here should really go to the Libcloud driver in
        libcloud.compute.drivers.dimensiondata.py _to_node()

        """

        element = self.region.connection.request_with_orgId_api_2(
            'server/server/%s' % node.id).object

        if element.find(fixxpath('networkInfo', TYPES_URN)) is None:
            return []

        interfaces = []
        for item in element.findall(fixxpath('networkInfo/additionalNic', TYPES_URN)):
            interfaces.append({'id': item.get('id'),
                'network': item.get('vlanName')})

        return interfaces

    def polish_blueprint(self, blueprint, polishers, container):
        """
        Walks a named blueprint for this facility and polish related resources

        :param blueprint: the blueprint to build
        :type blueprint: ``dict``

        :param polishers: polishers to be applied
        :type polishers: list of :class:`plumbery.PlumberyPolisher`

        :param container: where these nodes are located
        :type container: list of :class:`plumbery.PlumberyDomain`

        """

        if 'nodes' not in blueprint:
            return

        for item in blueprint['nodes']:

            if type(item) is dict:
                label = item.keys()[0]
                settings = item[label]
            else:
                label = str(item)
                settings = {}
            settings['name'] = label

            for label in self.expand_labels(label):

                logging.info("Polishing node '{}'".format(label))

                node = self.get_node(label)
                if node is None:
                    logging.info("- not found")
                    continue

                for polisher in polishers:
                    polisher.shine_node(node, settings, container)

    def start_blueprint(self, blueprint):
        """
        Starts nodes of a given blueprint at this facility

        :param blueprint: the blueprint to build
        :type blueprint: ``dict``

        """

        if 'nodes' not in blueprint:
            return

        for item in blueprint['nodes']:

            if type(item) is dict:
                label = item.keys()[0]

            else:
                label = item

            for label in self.expand_labels(label):
                self.start_node(label)

    def _start_monitoring(self, node, monitoring='ESSENTIALS'):
        """
        Enables monitoring of one node

        :param node: the target node
        :type node: :class:`libcloud.compute.base.Node`

        :param monitoring: either 'ESSENTIALS' or 'ADVANCED'
        :type monitoring: ``str``

        """

        value = monitoring.upper()
        logging.info("Starting {} monitoring of node '{}'".format(value.lower(), node.name))

        if value not in ['ESSENTIALS', 'ADVANCED']:
            logging.info("- monitoring should be either 'essentials' or 'advanced'")
        else:
            while True:
                try:
                    self.region.ex_enable_monitoring(node, service_plan=value)
                    logging.info("- in progress")
                    return True

                except Exception as feedback:
                    if 'RESOURCE_BUSY' in str(feedback):
                        time.sleep(10)
                        continue

                    elif 'RETRYABLE_SYSTEM_ERROR' in str(feedback):
                        time.sleep(10)
                        continue

                    elif 'NO_CHANGE' in str(feedback):
                        logging.info("- already done")

                    else:
                        logging.info("- unable to start monitoring")
                        logging.info(str(feedback))

                break

        return False

    def start_node(self, name):
        """
        Starts one node

        :param name: the name of the target node
        :type name: ``str``

        """

        node = self.get_node(name)

        if self.plumbery.safeMode:
            logging.info("Would have started node '{}' if not in safe mode"
                                                                .format(name))
            return

        logging.info("Starting node '{}'".format(name))
        if node is None:
            logging.info("- not found")
            return

        while True:

            try:
                self.region.ex_start_node(node)
                logging.info("- in progress")

            except Exception as feedback:

                if 'RESOURCE_BUSY' in str(feedback):
                    time.sleep(10)
                    continue

                elif 'SERVER_STARTED' in str(feedback):
                    logging.info("- skipped - node is up and running")

                else:
                    logging.info("- unable to start node")
                    logging.info(str(feedback))

            break

        return

    def stop_blueprint(self, blueprint):
        """
        Stops nodes of the given blueprint at this facility

        :param blueprint: the blueprint to build
        :type blueprint: ``dict``

        You can use the following setting to prevent plumbery from stopping a
        node::

          - sql:
              domain: *vdc1
              ethernet: *data
              nodes:
                - slaveSQL:
                    running: always

        """

        if 'nodes' not in blueprint:
            return

        for item in blueprint['nodes']:

            if type(item) is dict:
                label = item.keys()[0]
                settings = item.values()[0]

            else:
                label = item
                settings = {}

            for label in self.expand_labels(label):

                if 'running' in settings and settings['running'] == 'always':
                    logging.info("Node '{}' has to stay always on".format(label))
                    continue

                if self.plumbery.safeMode:
                    logging.info("Would have stopped node '{}' "
                                    "if not in safe mode".format(label))
                    continue

                node = self.get_node(label)

                logging.info("Stopping node '{}'".format(label))

                if node is None:
                    logging.info("- not found")
                    continue

                else:

                    while True:

                        try:
                            self.region.ex_shutdown_graceful(node)
                            logging.info("- in progress")

                        except Exception as feedback:

                            if 'RESOURCE_BUSY' in str(feedback):
                                time.sleep(10)
                                continue

                            elif 'UNEXPECTED_ERROR' in str(feedback):
                                time.sleep(10)
                                continue

                            elif 'SERVER_STOPPED' in str(feedback):
                                logging.info("- skipped - node is already stopped")

                            else:
                                logging.info("- unable to stop node")
                                logging.info(str(feedback))

                        break

    def _stop_monitoring(self, node, settings):
        """
        Disables monitoring of one node

        :param node: the target node
        :type node: :class:`libcloud.compute.base.Node`

        """

        if node is None:
            return

        if 'running' in settings and settings['running'] == 'always':
            return

        while True:

            try:
                self.region.ex_disable_monitoring(node)
                logging.info("Stopping monitoring of node '{}'"
                                                        .format(node.name))
                logging.info("- in progress")

            except Exception as feedback:

                if 'NO_CHANGE' in str(feedback):
                    pass

                elif 'OPERATION_NOT_SUPPORTED' in str(feedback):
                    pass

                elif 'RESOURCE_BUSY' in str(feedback):
                    time.sleep(10)
                    continue

                elif 'RESOURCE_LOCKED' in str(feedback):
                    logging.info("Stopping monitoring of node '{}'"
                                                        .format(node.name))
                    logging.info("- not now - locked")

                else:
                    logging.info("Stopping monitoring of node '{}'"
                                                        .format(node.name))
                    logging.info("- unable to stop monitoring")
                    logging.info(str(feedback))

            break

    def _update_ipv6(self, node):
        """
        Retrieves the ipv6 address for this node

        This is a hack. Code here should really go to the Libcloud driver in
        libcloud.compute.drivers.dimensiondata.py _to_node()

        """

        try:
            element = self.region.connection.request_with_orgId_api_2(
                'server/server/%s' % node.id).object

            has_network_info \
                = element.find(fixxpath('networkInfo', TYPES_URN)) is not None

            ipv6 = element.find(
                fixxpath('networkInfo/primaryNic', TYPES_URN)) \
                .get('ipv6') \
                if has_network_info else \
                element.find(fixxpath('nic', TYPES_URN)).get('ipv6')

            node.extra['ipv6'] = ipv6

        except Exception as feedback:

            if 'RESOURCE_NOT_FOUND' in str(feedback):
                node.extra['ipv6'] = ''

            else:
                logging.info("Error: unable to retrieve IPv6 addresses ")
                logging.info(str(feedback))
