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

from domain import PlumberyDomain
from nodes import PlumberyNodes

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

    # handle to the Apache Libcloud driver
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

        nodes = PlumberyNodes(self)
        nodes.build_blueprint(blueprint, domain)

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

        nodes = PlumberyNodes(self)
        nodes.destroy_blueprint(blueprint)

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

    def get_image(self, name):
        """
        Retrieves an acceptable image

        :param name: the name of the target image
        :type name: ``str``

        :returns: :class:`Image` - the target image, or None

        """

        for image in self._images:
            if name in image.name:
                return image

        return None

    def get_location_id(self):
        """
        Retrieves the id of the current location

        :return: ``str``- the id of the current location

        """

        return self.location.id

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

        nodes = PlumberyNodes(self)
        nodes.polish_blueprint(blueprint, polishers)

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

        nodes = PlumberyNodes(self)
        nodes.start_blueprint(blueprint)

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

        nodes = PlumberyNodes(self)
        nodes.stop_blueprint(blueprint)
