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
import time

from libcloud.compute.base import NodeAuthPassword

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
        nodes.build_blueprint(blueprint, domain)

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
        self.network = None
        self.domain = None

#    def __repr__(self):
#
#        return "<PlumberyNodes facility: {}>".format(self.facility)

    def build_blueprint(self, blueprint, domain):
        """
        Create missing nodes

        :param blueprint: the blueprint to build
        :type blueprint: ``dict``

        :param domain: the domain where nodes will be built
        :type domain: :class:`plumbery.PlumberyDomain`

        """

        self.facility.power_on()

        if 'nodes' not in blueprint:
            raise PlumberyException("Error: no nodes have been defined for the blueprint '{}'!".format(blueprint['target']))

        for item in blueprint['nodes']:

            if type(item) is dict:
                label = item.keys()[0]
                settings = item.values()[0]

            else:
                label = item
                settings = {}

            if self.get_node(label):
                logging.info("Node '{}' already exists".format(label))
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
                raise PlumberyException("Error: unable to find image for '{}'!".format(imageName))

            if self.plumbery.safeMode:
                logging.info("Would have created node '{}' "
                                "if not in safe mode".format(label))
                continue

            logging.info("Creating node '{}'".format(label))
            while True:

                try:
                    self.region.create_node(
                        name=label,
                        image=image,
                        auth=NodeAuthPassword(
                            self.plumbery.get_shared_secret()),
                        ex_network_domain=domain.domain,
                        ex_vlan=domain.network,
                        ex_is_started=False,
                        ex_description=description)
                    logging.info("- in progress")

                except Exception as feedback:

                    if 'RESOURCE_BUSY' in str(feedback):
                        time.sleep(10)
                        continue

                    else:
                        raise PlumberyException(
                            "Error: unable to create node '{0}' - {1}!".format(label, feedback))

                break

    def destroy_blueprint(self, blueprint):
        """
        Destroys nodes of a given blueprint

        :param blueprint: the blueprint to build
        :type blueprint: ``dict``

        """

        self.facility.power_on()

        if 'nodes' not in blueprint:
            return

        # destroy in reverse order
        for item in reversed(blueprint['nodes']):

            if type(item) is dict:
                label = item.keys()[0]
            else:
                label = str(item)

            node = self.get_node(label)
            if node is None:
                continue

            if self.plumbery.safeMode:
                logging.info("Would have destroyed node '{}' "
                                "if not in safe mode".format(label))
                continue

            logging.info("Destroying node '{}'".format(label))
            while True:

                try:
                    self.region.destroy_node(node)
                    logging.info("- in progress")

                except Exception as feedback:

                    if 'RESOURCE_BUSY' in str(feedback):
                        time.sleep(10)
                        continue

                    elif 'SERVER_STARTED' in str(feedback):
                        logging.info("- skipped - node is up and running")

                    else:
                        raise PlumberyException("Error: unable to destroy node '{0}' - {1}!".format(label, feedback))

                break

    def get_node(self, name):
        """
        Retrieves a node by name

        :param name: the name of the target node
        :type name: ``str``

        :returns: :class:`libcloud.compute.base.Node`
            - the target node, or None

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

            # found an existing node with this name
            if node.name == name:
                return node

        return None

    def polish_blueprint(self, blueprint, polishers):
        """
        Walks a named blueprint for this facility and polish related resources

        :param blueprint: the blueprint to build
        :type blueprint: ``dict``

        :param polishers: polishers to be applied
        :type polishers: list of :class:`plumbery.PlumberyPolisher`

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

            node = self.get_node(label)
            if node is not None:

                logging.info("Polishing node '{}'".format(node.name))

                for polisher in polishers:
                    polisher.shine_node(node, settings)

    def start_node(self, name, settings={}):
        """
        Starts one node

        :param name: the name of the target node
        :type name: ``str``

        :param settings: extracted from the fittings plan for this node
        :type settings: ``dict``

        :returns: the node itself

        """

        node = self.get_node(name)
        if node is None:
            return None

        if self.plumbery.safeMode:
            logging.info("Would have started node '{}' if not in safe mode".format(name))

        else:
            logging.info("Starting node '{}'".format(name))

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
                        raise PlumberyException("Error: unable to start node '{0}' - {1}!".format(name, feedback))

                break

        return node

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
                settings = item.values()[0]

            else:
                label = item
                settings = {}

            self.start_node(label, settings)

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

            if 'running' in settings and settings['running'] == 'always':
                logging.info("Node '{}' has to stay always on".format(label))
                continue

            node = self.get_node(label)
            if node is None:
                continue

            if self.plumbery.safeMode:
                logging.info("Would have stopped node '{}' if not in safe mode".format(label))

            else:
                logging.info("Stopping node '{}'".format(label))

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
                            raise PlumberyException("Error: unable to stop node '{0}' {1}!".format(label, feedback))

                    break
