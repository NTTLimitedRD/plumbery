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
import sys
import time

from libcloud.compute.base import NodeAuthPassword
from libcloud.compute.types import NodeState

from domain import PlumberyDomain
from polisher import PlumberyPolisher
from exceptions import PlumberyException

__all__ = ['PlumberyFacility']


class PlumberyFacility:
    """
    Plumbing at one facility

    :param plumbery: the automate that is coordinating
            plumbing activities at multiple facilities
    :type plumbery: :class:`plumbery.PlumberyEngine`

    :param fittings:  the plan for the fittings
    :type fittings: :class:`plumbery.PlumberyBlueprints`

    Example::

        from plumbery.facility import PlumberyFacility
        facility = PlumberyFacility(plumbery=plumbery, fittings=fittings)
        facility.build_all_blueprints()

    In this example a facility is ruled by the given plumber, and the plan
    of all the fittings is provided as well.

    Attributes:

        plumbery:
            global parameters and functions

        fittings:
            the plan is available when needed

    """

    # the description of the fittings
    fittings = None

    # the list of available images to create nodes
    images = None

    # the target physical data center
    location = None

    # the handle to global parameters and functions
    plumbery = None

    # the handle to the Apache Libcloud driver
    region = None

    def __init__(self, plumbery=None, fittings=None):
        """Puts this facility in context"""

        # handle to global parameters and functions
        self.plumbery = plumbery

        # parameters for this location
        self.fittings = fittings

        # configure the API endpoint - regional parameter is related to federated structure of cloud services at Dimension Data
        self.region = plumbery.driver(
            plumbery.get_user_name(),
            plumbery.get_user_password(),
            region=fittings.regionId)

        # focus at one specific location - and attempt to use the API over the network
        try:
            self.location = self.region.ex_get_location_by_id(fittings.locationId)
        except Exception as feedback:
            raise PlumberyException("Error: unable to communicate with API endpoint - have you checked http_proxy environment variable? - %s" % feedback)

        # fetch the list of available images only once from the API
        self.images = self.region.list_images(location=self.location)

    def build_all_blueprints(self):
        """
        Builds all blueprints defined for this facility

        """

        for blueprint in self.fittings.blueprints:
            logging.info("Building blueprint '{}'".format(blueprint.keys()[0]))
            self.build_blueprint(blueprint.keys()[0])

    def build_blueprint(self, name):
        """
        Builds a named blueprint for this facility

        :param name: the name of the blueprint to build
        :type name: ``str``

        """

        # get the blueprint
        blueprint = self.get_blueprint(name)
        if not blueprint:
            return

        # create the network domain if it does not exist
        domain = PlumberyDomain(self)
        domain.build(blueprint)

        # create nodes that do not exist
        self._build_nodes(blueprint=blueprint, domain=domain)

    def _build_nodes(self, blueprint, domain):
        """
        Create nodes if they do not exist at this facility

        :param blueprint: the blueprint to build
        :type blueprint: ``dict``

        :param domain: the domain where nodes will be built
        :type domain: :class:`plumbery.PlumberyDomain`

        """

        # ensure that we have some nodes described here
        if 'nodes' not in blueprint:
            raise PlumberyException("Error: no nodes have been defined for the blueprint '{}'!".format(blueprint['target']))

        # respect the order of nodes defined in the fittings description
        for item in blueprint['nodes']:

            # node has several explicit attributes
            if type(item) is dict:
                nodeName = item.keys()[0]
                nodeAttributes = item.values()[0]

            # node has only a name
            else:
                nodeName = item
                nodeAttributes = None

            # node may already exist
            if self.get_node(nodeName):
                logging.info("Node '{}' already exists".format(nodeName))

            # create a new node
            else:

                # the description attribute is a smart way to tag resources
                description = '#plumbery'
                if type(nodeAttributes) is dict and 'description' in nodeAttributes:
                    description = nodeAttributes['description'] + ' #plumbery'

                # define which appliance to use
                if type(nodeAttributes) is dict and 'appliance' in nodeAttributes:
                    imageName = nodeAttributes['appliance']
                else:
                    imageName = 'Ubuntu'

                # find suitable image to use
                image = None
                for image in self.images:
                    if imageName in image.name:
                        break

                # Houston, we've got a problem
                if image is None or imageName not in image.name:
                    raise PlumberyException("Error: unable to find image for '{}'!".format(imageName))

                # safe mode
                if self.plumbery.safeMode:
                    logging.info("Would have created node '{}' if not in safe mode".format(nodeName))

                # actual node creation
                else:
                    logging.info("Creating node '{}'".format(nodeName))

                    # we may have to wait for busy resources
                    while True:

                        try:
                            self.region.create_node(
                                name=nodeName,
                                image=image,
                                auth=NodeAuthPassword(
                                    self.plumbery.get_shared_secret()),
                                ex_network_domain=domain.domain,
                                ex_vlan=domain.network,
                                ex_is_started=False,
                                ex_description=description)
                            logging.info("- in progress")

                        except Exception as feedback:

                            # resource is busy, wait a bit and retry
                            if 'RESOURCE_BUSY' in str(feedback):
                                self.wait_and_tick()
                                continue

                            # fatal error
                            else:
                                raise PlumberyException(
                                    "Error: unable to create node '{0}' - {1}!".format(nodeName, feedback))

                        # quit the loop
                        break

    def destroy_all_nodes(self):
        """
        Destroys all nodes at this facility

        """

        # destroy in reverse order
        for blueprint in self.fittings.blueprints:
            self.destroy_nodes(blueprint.keys()[0])

    def destroy_nodes(self, name):
        """
        Destroys nodes of a given blueprint at this facility

        :param name: the name of the blueprint to destroy
        :type name: ``str``

        """

        # get the blueprint
        blueprint = self.get_blueprint(name)
        if not blueprint:
            return

        # ensure that some nodes have been described
        if 'nodes' not in blueprint:
            return

        # destroy in reverse order
        for item in reversed(blueprint['nodes']):

            # find the name of the node to be destroyed
            if type(item) is dict:
                nodeName = item.keys()[0]
            else:
                nodeName = str(item)

            # enumerate existing nodes
            node = self.get_node(nodeName)

            # destroy an existing node
            if node is not None:

                # safe mode
                if self.plumbery.safeMode:
                    logging.info("Would have destroyed node '{}' if not in safe mode".format(nodeName))

                # actual node destruction
                else:
                    logging.info("Destroying node '{}'".format(nodeName))

                    # we may have to wait for busy resources
                    while True:

                        try:
                            self.region.destroy_node(node)
                            logging.info("- in progress")

                        except Exception as feedback:

                            # resource is busy, wait a bit and retry
                            if 'RESOURCE_BUSY' in str(feedback):
                                self.wait_and_tick()
                                continue

                            # node is up and running, would have to stop it first
                            elif 'SERVER_STARTED' in str(feedback):
                                logging.info("- skipped - node is up and running")

                            # fatal error
                            else:
                                raise PlumberyException("Error: unable to destroy node '{0}' - {1}!".format(nodeName, feedback))


                        # quit the loop
                        break

    def focus(self):
        """Where are we plumbing?"""
        logging.info("Plumbing at '{}' {} ({})".format(self.location.id, self.location.name, self.location.country))

    def get_blueprint(self, name):
        """
        Retrieves a blueprint by name

        :param name: the name of the target blueprint
        :type name: ``str``

        :returns: ``dict`` - the target blueprint, or None

        """

        for blueprint in self.fittings.blueprints:
            if name in blueprint.keys()[0]:
                blueprint = blueprint[name]
                blueprint['target'] = name
                return blueprint

        return None

    def get_node(self, name):
        """
        Retrieves a node by name

        :param name: the name of the target node
        :type name: ``str``

        :returns: :class:`libcloud.compute.base.Node`
            - the target node, or None

        """

        # enumerate existing nodes
        node = None
        for node in self.region.list_nodes():

            # skip nodes from other locations
            if node.extra['datacenterId'] != self.location.id:
                continue

#           # skip nodes from other network domains
#           if node.extra['networkDomainId'] != self.domain.id:
#               continue

            # found an existing node with this name
            if node.name == name:
                return node

        # not found
        return None

    def polish_node(self, node, polisher):
        """
        Waits for a node to be started and polish it

        :param node: the target node
        :type node: :class:`libcloud.compute.base.Node`

        :param polisher: the polisher to apply
        :type polisher: :class:`plumbery.PlumberyPolisher`

        """

        # we have to wait until node is running
        while node is not None:
            if node.state == NodeState.RUNNING:
                break

            # give it some time to start
            PlumberyFacility.wait_and_tick()
            node = self.get_node(node.name)
            continue

        # polish
        if node:
            polisher.shine_node(node)

    def start_all_nodes(self):
        """
        Starts all nodes at this facility

        """

        for blueprint in self.fittings.blueprints:
            self.start_nodes(blueprint.keys()[0])

    def _start_node(self, name, attributes=None):
        """
        Starts one node

        :param name: the name of the target node
        :type name: ``str``

        :param attributes: additional attributes associated with this node
        :type attributes: ``dict``

        """

        # get fresh state of the node
        node = self.get_node(name)

        # not found
        if node is None:
            return None

        # define which polish to use
        polisher = None
        if type(attributes) is dict and 'polish' in attributes:
            polish = attributes['polish']
            polisher = PlumberyPolisher.from_shelf(polish)

        # safe mode
        if self.plumbery.safeMode:
            logging.info("Would have started node '{}' if not in safe mode".format(name))

        # actual node start
        else:
            logging.info("Starting node '{}'".format(name))

            # we may have to wait for busy resources
            while True:

                try:
                    self.region.ex_start_node(node)
                    logging.info("- in progress")

                    # if there is a need to polish the appliance, we may have to wait a bit more
                    if polisher:
                        self.polish_node(node, polisher)

                except Exception as feedback:

                    # resource is busy, wait a bit and retry
                    if 'RESOURCE_BUSY' in str(feedback):
                        self.wait_and_tick()
                        continue

                    # node is up and running, nothing to do
                    elif 'SERVER_STARTED' in str(feedback):
                        logging.info("- skipped - node is up and running")

                    # fatal error
                    else:
                        raise PlumberyException("Error: unable to start node '{0}' - {1}!".format(name, feedback))

                # quit the loop
                break

        # provide more details
        return node

    def start_nodes(self, name):
        """
        Starts nodes from a given blueprint at this facility

        :param name: the name of the target blueprint
        :type name: ``str``

        """

        # get the blueprint
        blueprint = self.get_blueprint(name)
        if not blueprint:
            return

        # ensure that some nodes have been described
        if 'nodes' not in blueprint:
            return

        # start nodes
        for item in blueprint['nodes']:

            # node has several explicit attributes
            if type(item) is dict:
                nodeName = item.keys()[0]
                nodeAttributes = item.values()[0]

            # node has only a name
            else:
                nodeName = item
                nodeAttributes = None

            # one node at at time
            self._start_node(nodeName, nodeAttributes)

    def stop_all_nodes(self):
        """
        Stops all nodes at this facility

        """

        for blueprint in self.fittings.blueprints:
            self.stop_nodes(blueprint.keys()[0])

    def stop_nodes(self, name):
        """
        Stops nodes of the given blueprint at this facility

        :param name: the name of the target blueprint
        :type name: ``str``

        """

        # get the blueprint
        blueprint = self.get_blueprint(name)
        if not blueprint:
            return

        # ensure that some nodes have been described
        if 'nodes' not in blueprint:
            return

        # stop nodes
        for item in blueprint['nodes']:

            # find the name of the node to be destroyed
            if type(item) is dict:
                nodeName = item.keys()[0]
            else:
                nodeName = str(item)

            # enumerate existing nodes
            node = self.get_node(nodeName)

            # stop an existing node
            if node is not None:

                # safe mode
                if self.plumbery.safeMode:
                    logging.info("Would have stopped node '{}' if not in safe mode".format(nodeName))

                # actual node stop
                else:
                    logging.info("Stopping node '{}'".format(nodeName))

                    # we may have to wait for busy resources
                    while True:

                        try:
                            self.region.ex_shutdown_graceful(node)
                            logging.info("- in progress")

                        except Exception as feedback:

                            # resource is busy, wait a bit and retry
                            if 'RESOURCE_BUSY' in str(feedback):
                                self.wait_and_tick()
                                continue

                            # transient error, wait a bit and retry
                            elif 'UNEXPECTED_ERROR' in str(feedback):
                                self.wait_and_tick()
                                continue

                            # node is already stopped
                            elif 'SERVER_STOPPED' in str(feedback):
                                logging.info("- skipped - node is already stopped")

                            # fatal error
                            else:
                                raise PlumberyException("Error: unable to stop node '{0}' {1}!".format(nodeName, feedback))

                        # quit the loop
                        break

    @staticmethod
    def wait_and_tick(tick=3):
        """Animate the screen while delaying next call to the API"""

        sys.stdout.write('-\r')
        sys.stdout.flush()
        time.sleep(tick)
        sys.stdout.write('\\\r')
        sys.stdout.flush()
        time.sleep(tick)
        sys.stdout.write('|\r')
        sys.stdout.flush()
        time.sleep(tick)
        sys.stdout.write('/\r')
        sys.stdout.flush()
        time.sleep(tick)
        sys.stdout.write(' \r')
