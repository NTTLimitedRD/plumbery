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

# standard libraries
import sys
import time

# Apache Libcloud - https://libcloud.readthedocs.org/en/latest
from libcloud.compute.base import NodeAuthPassword
from libcloud.compute.types import NodeState

# other code related to plumbery
from domain import PlumberyDomain
from polisher import PlumberyPolisher
from exceptions import PlumberyException

__all__ = ['PlumberyFacility']


class PlumberyFacility:
    """Plumbing at one facility

    Args:

        plumbery (PlumberyEngine): the automate that is coordinating
            plumbing activities at multiple facilities

        fittings (PlumberyBlueprints): the plan for the fittings

    Example::

        from plumbery.facility import PlumberyFacility
        facility = PlumberyFacility(plumbery=plumbery, fittings=fittings)
        facility.build_all_blueprints()

    In this example a facility is ruled by the given plumber, and the plan
    of all the fittings is provided as well.

    Attributes:

        plumbery: global parameters and functions

        fittings: the plan is available when needed

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

    def __init__(self, plumbery=None, fittings=None, logger=None):
        """Put this facility in context"""

        # handle to global parameters and functions
        self.plumbery = plumbery

        # consumer can pass callable logger where all messages will be sent.
        self.logger = logger if logger is not None else sys.stdout.write

        # parameters for this location
        self.fittings = fittings

        # configure the API endpoint - regional parameter is related to federated structure of cloud services at Dimension Data
        self.region = plumbery.driver(plumbery.userName, plumbery.userPassword, region=fittings.regionId)

        # focus at one specific location - and attempt to use the API over the network
        try:
            self.location = self.region.ex_get_location_by_id(fittings.locationId)
        except Exception as feedback:
            raise PlumberyException("Error: unable to communicate with API endpoint - have you checked http_proxy environment variable? - %s" % feedback)

        # fetch the list of available images only once from the API
        self.images = self.region.list_images(location=self.location)

    def build_all_blueprints(self):
        """Build all blueprints"""

        for blueprint in self.fittings.blueprints:
            self.logger("Building blueprint '{}'".format(blueprint.keys()[0]))
            self.build_blueprint(blueprint.keys()[0])

    def build_blueprint(self, name):
        """Build a named blueprint"""

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
        """Create nodes if they do not exist"""

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
                self.logger("Node '{}' already exists".format(nodeName))

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
                    self.logger("Would have created node '{}' if not in safe mode".format(nodeName))

                # actual node creation
                else:
                    self.logger("Creating node '{}'".format(nodeName))

                    # we may have to wait for busy resources
                    while True:

                        try:
                            self.region.create_node(
                                name=nodeName,
                                image=image,
                                auth=NodeAuthPassword(self.plumbery.sharedSecret),
                                ex_network_domain=domain.domain,
                                ex_vlan=domain.network,
                                ex_is_started=False,
                                ex_description=description)
                            self.logger("- in progress")

                        except Exception as feedback:

                            # resource is busy, wait a bit and retry
                            if 'RESOURCE_BUSY' in str(feedback):
                                self.wait_and_tick()
                                continue

                            # fatal error
                            else:
                                raise PlumberyException(
                                    "Error: unable to create node '{1}' - {2}!".format(nodeName, feedback))

                        # quit the loop
                        break

    def destroy_all_nodes(self):
        """Destroy all nodes"""

        # destroy in reverse order
        for blueprint in self.fittings.blueprints:
            self.destroy_nodes(blueprint.keys()[0])

    def destroy_nodes(self, name):
        """Destroy nodes"""

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
                    self.logger("Would have destroyed node '{}' if not in safe mode".format(nodeName))

                # actual node destruction
                else:
                    self.logger("Destroying node '{}'".format(nodeName))

                    # we may have to wait for busy resources
                    while True:

                        try:
                            self.region.destroy_node(node)
                            self.logger("- in progress")

                        except Exception as feedback:

                            # resource is busy, wait a bit and retry
                            if 'RESOURCE_BUSY' in str(feedback):
                                self.wait_and_tick()
                                continue

                            # node is up and running, would have to stop it first
                            elif 'SERVER_STARTED' in str(feedback):
                                self.logger("- skipped - node is up and running")

                            # fatal error
                            else:
                                raise PlumberyException("Error: unable to destroy node '{1}' - {2}!".format(nodeName, feedback))


                        # quit the loop
                        break

    def focus(self):
        """Where are we plumbing?"""
        self.logger("Plumbing at '{}' {} ({})".format(self.location.id, self.location.name, self.location.country))

    def get_blueprint(self, name):
        """Get a blueprint by name"""

        for blueprint in self.fittings.blueprints:
            if name in blueprint.keys()[0]:
                blueprint = blueprint[name]
                blueprint['target'] = name
                return blueprint

        return None

    def get_node(self, name):
        """Get a node by name"""

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
        """Wait for a node to be started and polish it"""

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
        """Start all nodes"""

        for blueprint in self.fittings.blueprints:
            self.start_nodes(blueprint.keys()[0])

    def _start_node(self, name, attributes=None):
        """Start a node"""

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
            self.logger("Would have started node '{}' if not in safe mode".format(name))

        # actual node start
        else:
            self.logger("Starting node '{}'".format(name))

            # we may have to wait for busy resources
            while True:

                try:
                    self.region.ex_start_node(node)
                    self.logger("- in progress")

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
                        self.logger("- skipped - node is up and running")

                    # fatal error
                    else:
                        raise PlumberyException("Error: unable to start node '{1}' - {2}!".format(name, feedback))

                # quit the loop
                break

        # provide more details
        return node

    def start_nodes(self, name):
        """Start nodes"""

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
        """Stop all nodes"""

        for blueprint in self.fittings.blueprints:
            self.stop_nodes(blueprint.keys()[0])

    def stop_nodes(self, name):
        """Stop nodes"""

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
                    self.logger("Would have stopped node '{}' if not in safe mode".format(nodeName))

                # actual node stop
                else:
                    self.logger("Stopping node '{}'".format(nodeName))

                    # we may have to wait for busy resources
                    while True:

                        try:
                            self.region.ex_shutdown_graceful(node)
                            self.logger("- in progress")

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
                                print("- skipped - node is already stopped")

                            # fatal error
                            else:
                                raise PlumberyException("Error: unable to stop node '{1}' {2}!".format(nodeName, feedback))

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
