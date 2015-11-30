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

__all__ = ['PlumberyFacility']


class PlumberyFacility:
    """
    Plumbing at one facility

    :param plumbery: the automate that is coordinating
            plumbing activities at multiple facilities
    :type plumbery: :class:`plumbery.PlumberyEngine`

    :param fittings:  the plan for the fittings
    :type fittings: :class:`plumbery.PlumberyFittings`

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

    fittings = None

    _images = []

    location = None

    plumbery = None

    # the handle to the Apache Libcloud driver
    region = None

    def __init__(self, plumbery=None, fittings=None):
        """Puts this facility in context"""

        self.plumbery = plumbery

        self.fittings = fittings

        # Dimension Data provides a federation of regions
        self.region = plumbery.provider(
            plumbery.get_user_name(),
            plumbery.get_user_password(),
            region=self.fittings.regionId)

    def __repr__(self):

        return "<PlumberyFacility fittings: {}>".format(self.fittings)

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

        blueprint = self.get_blueprint(name)
        if not blueprint:
            return

        domain = PlumberyDomain(self)
        domain.build(blueprint)

        self._build_nodes(blueprint=blueprint, domain=domain)

    def _build_nodes(self, blueprint, domain):
        """
        Create nodes if they do not exist at this facility

        :param blueprint: the blueprint to build
        :type blueprint: ``dict``

        :param domain: the domain where nodes will be built
        :type domain: :class:`plumbery.PlumberyDomain`

        """

        self.power_on()

        if 'nodes' not in blueprint:
            raise PlumberyException("Error: no nodes have been defined for the blueprint '{}'!".format(blueprint['target']))

        for item in blueprint['nodes']:

            if type(item) is dict:
                nodeName = item.keys()[0]
                nodeAttributes = item.values()[0]

            else:
                nodeName = item
                nodeAttributes = None

            if self.get_node(nodeName):
                logging.info("Node '{}' already exists".format(nodeName))

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
                for image in self._images:
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
                                time.sleep(10)
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

        self.power_on()

        blueprint = self.get_blueprint(name)
        if not blueprint:
            return

        if 'nodes' not in blueprint:
            return

        # destroy in reverse order
        for item in reversed(blueprint['nodes']):

            if type(item) is dict:
                nodeName = item.keys()[0]
            else:
                nodeName = str(item)

            node = self.get_node(nodeName)
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
                                time.sleep(10)
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
        """
        Where are we plumbing?

        """

        self.power_on()
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

        self.power_on()

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

        return None

    def polish_all_blueprints(self, polishers):
        """
        Walks all resources at this facility and polish them

        :param polishers: polishers to be applied
        :type polishers: list of :class:`plumbery.PlumberyPolisher`

        """

        for blueprint in self.fittings.blueprints:
            logging.info("Polishing blueprint '{}'".format(blueprint.keys()[0]))
            self.polish_blueprint(blueprint.keys()[0], polishers)

    def polish_blueprint(self, name, polishers):
        """
        Walks a named blueprint for this facility and polish related resources

        :param name: the name of the blueprint to polish
        :type name: ``str``

        :param polishers: polishers to be applied
        :type polishers: list of :class:`plumbery.PlumberyPolisher`

        """

        blueprint = self.get_blueprint(name)
        if not blueprint:
            return

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

    def power_on(self):
        """
        Switches electricity on

        """

        if not self.location:
            self.location = self.region.ex_get_location_by_id(self.fittings.locationId)

        # cache images to limit API calls
        if len(self._images) < 1:
            self._images = self.region.list_images(location=self.location)

    def start_all_nodes(self):
        """
        Starts all nodes at this facility

        """

        for blueprint in self.fittings.blueprints:
            self.start_nodes(blueprint.keys()[0])

    def _start_node(self, name, settings={}):
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

    def start_nodes(self, name):
        """
        Starts nodes from a given blueprint at this facility

        :param name: the name of the target blueprint
        :type name: ``str``

        """

        blueprint = self.get_blueprint(name)
        if not blueprint:
            return

        if 'nodes' not in blueprint:
            return

        for item in blueprint['nodes']:

            if type(item) is dict:
                label = item.keys()[0]
                settings = item.values()[0]

            else:
                label = item
                settings = {}

            self._start_node(label, settings)

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

        You can use the following setting to prevent plumbery from stopping a
        node::

          - sql:
              domain: *vdc1
              ethernet: *data
              nodes:
                - slaveSQL:
                    running: always

        """

        blueprint = self.get_blueprint(name)
        if not blueprint:
            return

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
