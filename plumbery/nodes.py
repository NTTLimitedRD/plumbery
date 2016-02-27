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
from libcloud.common.dimensiondata import DimensionDataServerCpuSpecification

from exception import PlumberyException
from infrastructure import PlumberyInfrastructure

__all__ = ['PlumberyNodes']


class PlumberyNodes(object):
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
        :type container: :class:`plumbery.PlumberyInfrastructure`

        """

        logging.debug("Building nodes of blueprint '{}'".format(
            blueprint['target']))

        self.facility.power_on()

        if ('nodes' not in blueprint
                or not isinstance(blueprint['nodes'], list)):

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

                logging.info("Creating node '{}'".format(label))

                if self.get_node(label):
                    logging.info("- already there")
                    continue

                description = '#plumbery'
                if 'description' in settings:
                    description = settings['description'] + ' #plumbery'

                if 'appliance' in settings:
                    imageName = settings['appliance']
                else:
                    imageName = 'Ubuntu'

                image = self.facility.get_image(imageName)
                if image is None:
                    raise PlumberyException("Error: unable to find image "
                                            "for '{}'!".format(imageName))
                logging.debug("- using image '{}'".format(image.name))

                cpu = None
                if 'cpu' in settings:
                    tokens = str(settings['cpu']).split(' ')
                    if len(tokens) < 2:
                        tokens.append('1')
                    if len(tokens) < 3:
                        tokens.append('standard')

                    if (int(tokens[0]) < 1
                            or int(tokens[0]) > 32):

                        logging.info("- cpu should be between 1 and 32")

                    elif (int(tokens[1]) < 1
                            or int(tokens[1]) > 2):

                        logging.info("- core per cpu should be either 1 or 2")

                    elif tokens[2].upper() not in ('STANDARD',
                                                   'HIGHPERFORMANCE'):

                        logging.info("- cpu speed should be either 'standard'"
                                     " or 'highspeed'")

                    else:
                        cpu = DimensionDataServerCpuSpecification(
                            cpu_count=tokens[0],
                            cores_per_socket=tokens[1],
                            performance=tokens[2].upper())
                        logging.debug("- assigning {} cpus".format(
                            cpu.cpu_count))
                        logging.debug("- core per cpu: {}".format(
                            cpu.cores_per_socket))
                        logging.debug("- cpu performance: {}".format(
                            cpu.performance.lower()))

                memory = None
                if 'memory' in settings:
                    memory = int(settings['memory'])
                    if memory < 1 or memory > 256:
                        logging.info("- memory should be between 1 and 256")
                        memory = None
                    else:
                        logging.debug("- assigning {} GB of memory".format(
                            memory))

                if self.plumbery.safeMode:
                    logging.info("- skipped - safe mode")
                    continue

                if container.domain is None:
                    logging.info("- missing network domain")
                    continue

                if container.network is None:
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
                            ex_cpu_specification=cpu,
                            ex_memory_gb=memory,
                            ex_is_started=False,
                            ex_description=description)
                        logging.info("- in progress")

                    except Exception as feedback:

                        if 'RESOURCE_BUSY' in str(feedback):
                            time.sleep(10)
                            continue

                        elif 'RESOURCE_NOT_FOUND' in str(feedback):
                            logging.info("- not now")
                            logging.error(str(feedback))

                        elif 'RESOURCE_LOCKED' in str(feedback):
                            logging.info("- not now - locked")
                            logging.error(str(feedback))

                        else:
                            logging.info("- unable to create node")
                            logging.error(str(feedback))

                    break

    def destroy_blueprint(self, blueprint):
        """
        Destroys nodes of a given blueprint

        :param blueprint: the blueprint to build
        :type blueprint: ``dict``

        """

        self.facility.power_on()

        infrastructure = PlumberyInfrastructure(self.facility)
        container = infrastructure.get_container(blueprint)

        if ('nodes' not in blueprint
                or not isinstance(blueprint['nodes'], list)):
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

                node = self.get_node(label)
                if node is None:
                    logging.info("Destroying node '{}'".format(label))
                    logging.info("- not found")
                    continue

                if 'destroy' in settings and settings['destroy'] == 'never':
                    logging.info("Destroying node '{}'".format(label))
                    logging.info("- this node can never be destroyed")
                    return False

                timeout = 300
                tick = 6
                while node.extra['status'].action == 'SHUTDOWN_SERVER':
                    time.sleep(tick)
                    node = self.get_node(label)
                    timeout -= tick
                    if timeout < 0:
                        break

                if node.state == NodeState.RUNNING:
                    logging.info("Destroying node '{}'".format(label))
                    logging.info("- skipped - node is up and running")
                    continue

                if self.plumbery.safeMode:
                    logging.info("Destroying node '{}'".format(label))
                    logging.info("- skipped - safe mode")
                    continue

                self._stop_monitoring(node, settings)
                self._detach_node(node, settings)
                container._detach_node_from_internet(node)
                container._remove_from_pool(node)

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
                            logging.error(str(feedback))

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

        if ('running' in settings
                and settings['running'] == 'always'
                and node.state == NodeState.RUNNING):

            return True

        for interface in self._list_secondary_interfaces(node):

            logging.info("Detaching node '{}' from network '{}'".format(
                node.name, interface['network']))

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
                        logging.info("- already there")

                    else:
                        logging.info("- unable to detach node")
                        logging.error(str(feedback))
                        return False

                break

        return True

    @classmethod
    def expand_labels(self, label):
        """
        Designates multiple nodes with a simple label

        :param label: the label to be expanded, e.g., ``server[1..2]_eu``
        :type label: ``str``

        :return: a list of names, e.g., ``['server1_eu', 'server2_eu']``
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

            label = matches.group(1)+str(index)+matches.group(4)
            if re.match("^[0-9a-zA-Z]([0-9a-zA-Z\-]{0,61}[0-9a-zA-Z])?$", label) is None:
                logger.warning("Warning: '{}' is not a valid hostname".format(label))

            labels.append(label)

        return labels

    def get_node(self, path):
        """
        Retrieves a node by name

        :param path: the name of the target node, or its location
        :type path: ``str`` or ``list``of ``str``

        :return: the target node, or None
        :rtype: :class:`libcloud.compute.base.Node`

        This function always make a real API call to get fresh state of the
        target node. Therefore, it can be used in loops where you monitor
        the evolution of the node during build or other change operation.

        This function searches firstly at the current facility. If the
        name is a complete path to a remote node, then plumbery looks
        there. If a different region is provided, then authentication is done
        against the related endpoint.

        For example if ``MyServer`` has been defined in a data centre in
        Europe::

            >>>infrastructure.get_ethernet('MyServer')
            >>>infrastructure.get_ethernet(['EU6', 'MyServer'])
            Looking for remote node 'EU6::MyServer'
            - found it
            >>>infrastructure.get_ethernet(['dd-eu', 'EU6', 'MyServer'])
            Looking for offshore node 'dd-eu::EU6::MyServer'
            - found it


        """

        if isinstance(path, str):
            path = path.split('::')

        node = None

        if len(path) == 1: # local name

            self.facility.power_on()

            for node in self.region.list_nodes():

                if node.extra['datacenterId'] != self.facility.get_location_id():
                    continue

                if node.name == path[0]:

                    self._enrich_node(node)
                    return node

        elif len(path) == 2: # different location, same region

            self.facility.power_on()

            try:
                remoteLocation = self.region.ex_get_location_by_id(path[0])
            except IndexError:
                logging.warning("'{}' is unknown".format(path[0]))
                return None

            logging.debug("Looking for remote node '{}'"
                         .format('::'.join(path)))

            for node in self.region.list_nodes():

                if node.extra['datacenterId'] != path[0]:
                    continue

                if node.name == path[1]:

                    logging.debug("- found it")

                    self._enrich_node(node)
                    return node

        elif len(path) == 3: # other region

            offshore = self.plumbery.get_compute_driver(region=path[0])

            try:
                remoteLocation = offshore.ex_get_location_by_id(path[1])
            except IndexError:
                logging.warning("'{}' is unknown".format(path[1]))
                return None

            logging.debug("Looking for offshore node '{}'"
                         .format('::'.join(path)))

            for node in offshore.list_nodes():

                if node.extra['datacenterId'] != path[1]:
                    continue

                if node.name == path[2]:

                    logging.debug("- found it")

                    self._enrich_node(node)
                    return node

        return None

    def _enrich_node(self, node):
        """
        Adds attributes to a node

        This function is a hack, aiming to complement the nice job done by
        Libcloud:
        - add public IPv4 if one exists
        - add disk size, ids, etc.

        """

        # hack because the driver does not report public ipv4 accurately
        if len(node.public_ips) < 1:
            domain = self.region.ex_get_network_domain(
                node.extra['networkDomainId'])
            for rule in self.region.ex_list_nat_rules(domain):
                if rule.internal_ip == node.private_ips[0]:
                    node.public_ips.append(rule.external_ip)
                    break

        # hack to retrieve disk information
        node.extra['disks'] = []
        try:
            element = self.region.connection.request_with_orgId_api_2(
                'server/server/%s' % node.id).object

            for disk in findall(element, 'disk', TYPES_URN):
                scsiId = int(disk.get('scsiId'))
                speed = disk.get('speed')
                id = disk.get('id')
                sizeGb = int(disk.get('sizeGb'))
                node.extra['disks'].append({
                    'scsiId': scsiId,
                    'speed': speed,
                    'id': id,
                    'size': sizeGb
                    })

        except Exception as feedback:

            if 'RESOURCE_NOT_FOUND' in str(feedback):
                pass

            else:
                logging.info("Error: unable to retrieve storage information")
                logging.error(str(feedback))

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

                else:
                    label = str(item)

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
        items = element.findall(
            fixxpath('networkInfo/additionalNic', TYPES_URN))
        for item in items:
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
        :type container: list of :class:`plumbery.PlumberyInfrastructure`

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

            for label in self.expand_labels(label):

                node = self.get_node(label)
                settings['name'] = label

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
        logging.info("Starting {} monitoring of node '{}'".format(
            value.lower(), node.name))

        if value not in ['ESSENTIALS', 'ADVANCED']:
            logging.info("- monitoring should be "
                         "either 'essentials' or 'advanced'")
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
                        logging.info("- already there")

                    elif 'RESOURCE_LOCKED' in str(feedback):
                        logging.info("- unable to start monitoring "
                                     "- node has been locked")

                    else:
                        logging.info("- unable to start monitoring")
                        logging.error(str(feedback))

                break

        return False

    def start_node(self, node):
        """
        Starts one node

        :param node: the target node, or its name
        :type node: :class:`Node` or ``str``

        """

        if isinstance(node, str):
            name = node
            node = self.get_node(name)
        else:
            name = node.name

        logging.info("Starting node '{}'".format(name))
        if node is None:
            logging.info("- not found")
            return

        if self.plumbery.safeMode:
            logging.info("- skipped - safe mode")
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
                    logging.error(str(feedback))

            break

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
                self.stop_node(label, settings)

    def stop_node(self, node, settings={}):
        """
        Stops one node

        :param node: the target node, or its name
        :type node: :class:`Node` or ``str``

        :param settings: additional attributes for this node
        :type settings: ``dict``

        """

        if isinstance(node, str):
            name = node
            node = self.get_node(name)
        else:
            name = node.name

        logging.info("Stopping node '{}'".format(name))
        if node is None:
            logging.info("- not found")
            return

        if ('running' in settings
                and settings['running'] == 'always'
                and node.state == NodeState.RUNNING):

            logging.info("- skipped - node has to stay always on")
            return

        if self.plumbery.safeMode:
            logging.info("- skipped - safe mode")
            return

        retry = True
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

                elif 'VMWARE_TOOLS_INVALID_STATUS' in str(feedback):

                    # prevent transient errors
                    if retry:
                        retry = False
                        time.sleep(30)
                        continue

                    logging.info("- unable to shutdown gracefully "
                                 "- invalid VMware tools")

                    logging.info("- powering the node off")
                    try:
                        self.region.ex_power_off(node)
                        logging.info("- in progress")

                    except Exception as feedback:

                        if 'SERVER_STOPPED' in str(feedback):
                            logging.info("- already stopped")

                        else:
                            logging.info("- unable to stop node")
                            logging.error(str(feedback))

                elif 'SERVER_STOPPED' in str(feedback):
                    logging.info("- already stopped")

                else:
                    logging.info("- unable to stop node")
                    logging.error(str(feedback))

            break

    def _stop_monitoring(self, node, settings):
        """
        Disables monitoring of one node

        :param node: the target node
        :type node: :class:`libcloud.compute.base.Node`

        """

        if node is None:
            return

        if ('running' in settings
                and settings['running'] == 'always'
                and node.state == NodeState.RUNNING):

            return

        if self.plumbery.safeMode:
            return

        logging.info("Stopping monitoring of node '{}'".format(node.name))

        while True:

            try:
                self.region.ex_disable_monitoring(node)
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
                    logging.info("- not now - locked")

                else:
                    logging.info("- unable to stop monitoring")
                    logging.error(str(feedback))

            break
