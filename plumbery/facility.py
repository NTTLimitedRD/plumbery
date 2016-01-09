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

import socket
import logging

from exception import PlumberyException
from infrastructure import PlumberyInfrastructure
from nodes import PlumberyNodes

__all__ = ['PlumberyFacility', 'PlumberyFittings']


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

    def __init__(self, plumbery=None, fittings=None):
        """Puts this facility in context"""

        self.plumbery = plumbery

        self.fittings = fittings

        # first call to the API is done in self.power_on()
        self.region = None
        self.location = None

        self._cache_images = []
        self._cache_network_domains = []
        self._cache_vlans = []

    def __repr__(self):

        return "<PlumberyFacility fittings: {}>".format(self.fittings)

    def get_location_id(self):
        """
        Retrieves the id of the current location

        :return:  the id of the current location, e.g., 'EU7' or 'NA9'
        :rtype: ``str``

        """

        self.power_on()
        return self.location.id

    def list_basement(self):
        """
        Retrieves a list of blueprints that, together, constitute the basement
        of this facility

        :return: names of basement blueprints
        :rtype: ``list`` of ``str`` or ``[]``

        Basement is a list of blueprints defined in the fittings plan, as per
        following example::

            ---
            basement: admin control

            blueprints:

              - admin:
                  ...

        In that case you would get::

            >>facility.list_basement()
            ['admin', 'control']

        """

        if self.fittings.basement is None:
            return []

        return self.expand_blueprint(self.fittings.basement)

    def list_blueprints(self):
        """
        Retrieves a list of blueprints that have been defined

        :return: names of blueprints defined for this facility
        :rtype: ``list`` of ``str`` or ``[]``

        Blueprints are defined in the fittings plan, as per
        following example::

            ---
            blueprints:

              - admin:
                  ...

              - app: web data

              - web:
                  ...

              - data:
                  ...

        In that case you would get::

            >>facility.list_blueprints()
            ['admin', 'web', 'data']

        Note::
          As shown in the example above, only actionable blueprints are
          listed by this function.
        """

        names = []
        for blueprint in self.fittings.blueprints:
            name = blueprint.keys()[0]
            if not isinstance(blueprint[name], dict):
                continue
            if name in names:
                logging.warning("Duplicated blueprint name '{}'".format(name))
            else:
                names.append(name)

        return names

    def expand_blueprint(self, labels):
        """
        Designates multiple blueprints with a simple label

        :param labels: the label(s) to be expanded
        :type labels: ``str`` or ``list`` of ``str``

        :return: a list of names
        :rtype: ``list`` of ``str``

        Blueprints are defined in the fittings plan, as per
        following example::

            ---
            blueprints:

              - mongo: mongo_config mongo_mongos mongo_shard

              - mongo_config:
                  ...

              - mongo_mongos:
                  ...

              - mongo_shard:
                  ...

        In that case you would get::

            >>facility.expand_blueprint('mongo')
            ['mongo_config', 'mongo_mongos', 'mongo_shard']

            >>facility.expand_blueprint('mongo_config')
            ['mongo_config']

            >>facility.expand_blueprint('mongo_config mongo_mongos')
            ['mongo_config', 'mongo_mongos']

            >>facility.expand_blueprint(['mongo_config', 'alien_mongos'])
            ['mongo_config']

        """

        names = []

        if isinstance(labels, str):
            labels = labels.split(' ')

        for label in labels:

            for blueprint in self.fittings.blueprints:

                name = blueprint.keys()[0]
                if name != label:
                    continue

                if isinstance(blueprint[name], dict):
                    if label not in names:
                        names.append(label)
                else:
                    for token in str(blueprint[name]).split(' '):
                        if token not in names:
                            names.append(token)

        if names != labels:
            logging.info("Expanding '{}' to '{}'".format(
                ' '.join(labels), "', '".join(names)))

        return names

    def get_blueprint(self, name):
        """
        Retrieves a blueprint by name

        :param name: the name of the target blueprint
        :type name: ``str``

        :return: the blueprint with this name
        :rtype: ``dict`` or ``None``

        """

        for blueprint in self.fittings.blueprints:
            if name == blueprint.keys()[0]:
                blueprint = blueprint[name]
                blueprint['target'] = name
                return blueprint

        return None

    def list_domains(self):
        """
        Retrieves the list of network domains that have been defined across
        blueprints for this facility

        :return: names of network domains defined for this facility
        :rtype: ``list`` of ``str`` or ``[]``

        Domains are defined in blueprints. Usually fittings plan are using at
        least one network domain, sometimes several.

        """

        labels = set()
        for blueprint in self.fittings.blueprints:
            name = blueprint.keys()[0]
            if 'domain' in blueprint[name]:
                labels.add(blueprint[name]['domain'])

        return list(labels)

    def list_ethernets(self):
        """
        Retrieves the list of Ethernet networks that have been defined across
        blueprints for this facility

        :return: names of Ethernet networks defined for this facility
        :rtype: ``list`` of ``str`` or ``[]``

        Ethernet networks are defined in blueprints. Usually fittings plan are
        using at least one Ethernet network, often several.

        """

        labels = set()
        for blueprint in self.fittings.blueprints:
            name = blueprint.keys()[0]
            if 'ethernet' in blueprint[name]:
                labels.add(blueprint[name]['ethernet'])

        return list(labels)

    def list_nodes(self):
        """
        Retrieves the list of nodes that have been defined across
        blueprints for this facility

        :return: names of nodes defined for this facility
        :rtype: ``list`` of ``str`` or ``[]``

        Nodes are defined in blueprints.

        """

        labels = []
        for blueprint in self.fittings.blueprints:
            name = blueprint.keys()[0]
            if 'nodes' in blueprint[name]:
                for item in blueprint[name]['nodes']:
                    if type(item) is dict:
                        label = item.keys()[0]

                    else:
                        label = item

                    for label in PlumberyNodes.expand_labels(label):
                        if label in labels:
                            logging.warning("Duplicate node name '{}'"
                                            .format(label))
                        else:
                            labels.append(label)

        return labels

    def get_image(self, name):
        """
        Retrieves an acceptable image

        :param name: the name of the target image
        :type name: ``str``

        :return: a suitable image
        :rtype: :class:`Image` or ``None``

        This function looks at the library of available images and picks up
        the first image that has the name in it.

        Some examples::

            >>>facility.get_image('RedHat')
            ...
            >>>facility.get_image('RedHat 6 64-bit 4 CPU')
            ...

        """

        # cache images to limit API calls
        if len(self._cache_images) < 1:
            self.power_on()
            self._cache_images = \
                self.region.list_images(location=self.location)

        for image in self._cache_images:
            if name in image.name:
                return image

        return None

    def focus(self):
        """
        Where are we plumbing?

        """

        self.power_on()
        logging.info("Plumbing at '{}' {} ({})".format(
            self.location.id,
            self.location.name,
            self.location.country))

        blueprints = self.list_blueprints()
        if len(blueprints) < 1:
            logging.warning("- no blueprint has been found")
        else:
            logging.debug("- available blueprints: {}".format(
                "'"+"', '".join(blueprints)+"'"))

        basement = self.list_basement()
        if len(basement) > 0:
            logging.debug("- basement: {}".format(
                "'"+"', '".join(basement)+"'"))

    def power_on(self):
        """
        Switches electricity on

        """

        try:
            if self.region is None:
                logging.debug("Getting driver for '{}'".format(
                    self.fittings.regionId))
                self.region = self.plumbery.get_compute_driver(
                    region=self.fittings.regionId)

            if self.location is None:
                logging.debug("Getting location '{}'".format(
                    self.fittings.locationId))
                locations = []
                for location in self.region.list_locations():
                    locations.append(location.id)
                    if location.id == self.fittings.locationId:
                        self.location = location

                if self.location is None:
                    logging.debug("Known locations: {}".format(locations))
                    raise PlumberyException("Unknown location '{}'"
                                            .format(self.fittings.locationId))

        except ValueError:
            raise PlumberyException("Unknown region '{}'"
                                    .format(self.fittings.regionId))

        except socket.gaierror:
            raise PlumberyException("Cannot communicate with the API endpoint")

    def build_all_blueprints(self):
        """
        Builds all blueprints defined for this facility

        This function builds all network domains across all blueprints, then
        it builds all nodes across all blueprints.

        If the keyword ``basement`` mentions one or several blueprints,
        then these are built before the other blueprints.

        """

        self.power_on()
        infrastructure = PlumberyInfrastructure(self)
        nodes = PlumberyNodes(self)

        basement = self.list_basement()
        for name in basement:
            blueprint = self.get_blueprint(name)
            infrastructure.build(blueprint)

        blueprints = self.list_blueprints()
        for name in blueprints:
            if name not in basement:
                blueprint = self.get_blueprint(name)
                infrastructure.build(blueprint)

        for name in basement:
            blueprint = self.get_blueprint(name)
            container = infrastructure.get_container(blueprint)
            nodes.build_blueprint(blueprint, container)

        for name in blueprints:
            if name not in basement:
                blueprint = self.get_blueprint(name)
                container = infrastructure.get_container(blueprint)
                nodes.build_blueprint(blueprint, container)

    def build_blueprint(self, names):
        """
        Builds a named blueprint for this facility

        :param names: the name(s) of the blueprint(s) to build
        :type names: ``str`` or ``list`` of ``str``

        This function builds the named blueprint in two steps: the
        infrastructure comes first, and then the nodes themselves.

            >>>facility.build_blueprint('sql')

        If the keyword ``basement`` mentions one or several blueprints,
        then network domains of these special blueprints are built before
        the actual target blueprint.

        Example ``fittings.yaml``::

            ---
            basement: admin

            blueprints:

              - admin:
                  ethernet: control

              - sql:
                  ethernet: data
                  nodes:
                    - server1:
                        glue: control

        In this example, the node ``server1``has two network interfaces. The
        main network interface is connected to the network ``data``, and the
        secondary network interface is connected to the network ``control``.

        """

        self.power_on()
        infrastructure = PlumberyInfrastructure(self)
        nodes = PlumberyNodes(self)

        basement = self.list_basement()
        for name in basement:
            blueprint = self.get_blueprint(name)
            infrastructure.build(blueprint)

        for name in self.expand_blueprint(names):

            blueprint = self.get_blueprint(name)

            if name not in basement:
                infrastructure.build(blueprint)

            nodes.build_blueprint(
                blueprint,
                infrastructure.get_container(blueprint))

    def destroy_all_blueprints(self):
        """
        Destroys all blueprints at this facility

        """

        self.power_on()
        nodes = PlumberyNodes(self)
        infrastructure = PlumberyInfrastructure(self)

        basement = self.list_basement()

        for name in self.list_blueprints():
            if name in basement:
                continue
            blueprint = self.get_blueprint(name)
            logging.info("Destroying blueprint '{}'".format(name))
            nodes.destroy_blueprint(blueprint)
            infrastructure.destroy_blueprint(blueprint)

        for name in basement:
            blueprint = self.get_blueprint(name)
            logging.info("Destroying blueprint '{}'".format(name))
            nodes.destroy_blueprint(blueprint)
            infrastructure.destroy_blueprint(blueprint)

    def destroy_all_nodes(self):
        """
        Destroys all nodes at this facility

        """

        self.power_on()
        nodes = PlumberyNodes(self)

        basement = self.list_basement()

        for name in self.list_blueprints():
            if name in basement:
                continue
            blueprint = self.get_blueprint(name)
            logging.info("Destroying nodes of blueprint '{}'".format(name))
            nodes.destroy_blueprint(blueprint)

        for name in basement:
            blueprint = self.get_blueprint(name)
            logging.info("Destroying nodes of blueprint '{}'".format(name))
            nodes.destroy_blueprint(blueprint)

    def destroy_blueprint(self, names):
        """
        Destroys a given blueprint at this facility

        :param names: the name(s) of the blueprint(s) to destroy
        :type names: ``str`` or ``list`` of ``str``

        """

        self.power_on()
        nodes = PlumberyNodes(self)
        infrastructure = PlumberyInfrastructure(self)

        for name in self.expand_blueprint(names):

            blueprint = self.get_blueprint(name)
            nodes.destroy_blueprint(blueprint)
            infrastructure.destroy_blueprint(blueprint)

    def destroy_nodes(self, names):
        """
        Destroys nodes of a given blueprint at this facility

        :param names: the names of the blueprint to destroy
        :type names: ``str`` or ``list`` of ``str``

        """

        self.power_on()
        nodes = PlumberyNodes(self)

        for name in self.expand_blueprint(names):

            blueprint = self.get_blueprint(name)
            nodes.destroy_blueprint(blueprint)

    def polish_all_blueprints(self, polishers):
        """
        Walks all resources at this facility and polish them

        :param polishers: polishers to be applied
        :type polishers: list of :class:`plumbery.PlumberyPolisher`

        """

        basement = self.list_basement()
        for name in basement:
            logging.debug("Polishing blueprint '{}'".format(name))
            self.polish_blueprint(name, polishers)

        for name in self.list_blueprints():
            if name not in basement:
                logging.debug("Polishing blueprint '{}'".format(name))
                self.polish_blueprint(name, polishers)

    def polish_blueprint(self, names, polishers):
        """
        Walks a named blueprint for this facility and polish related resources

        :param names: the name(s) of the blueprint(s) to polish
        :type names: ``str`` or ``list`` of ``str``

        :param polishers: polishers to be applied
        :type polishers: list of :class:`plumbery.PlumberyPolisher`

        """

        self.power_on()
        infrastructure = PlumberyInfrastructure(self)
        nodes = PlumberyNodes(self)

        for name in self.expand_blueprint(names):

            blueprint = self.get_blueprint(name)

            container = infrastructure.get_container(blueprint)

            for polisher in polishers:
                polisher.shine_container(container)

            nodes.polish_blueprint(blueprint, polishers, container)

    def start_all_nodes(self):
        """
        Starts all nodes at this facility

        """

        basement = self.list_basement()
        for name in basement:
            self.start_nodes(name)

        for name in self.list_blueprints():
            if name not in basement:
                self.start_nodes(name)

    def start_nodes(self, names):
        """
        Starts nodes from a given blueprint at this facility

        :param names: the name(s) of the target blueprint(s)
        :type names: ``str`` or ``list`` of ``str``

        """

        nodes = PlumberyNodes(self)

        for name in self.expand_blueprint(names):

            blueprint = self.get_blueprint(name)

            if 'nodes' not in blueprint:
                continue

            nodes.start_blueprint(blueprint)

    def stop_all_nodes(self):
        """
        Stops all nodes at this facility

        """

        basement = self.list_basement()

        for name in self.list_blueprints():
            if name not in basement:
                self.stop_nodes(name)

        for name in basement:
            self.stop_nodes(name)

    def stop_nodes(self, names):
        """
        Stops nodes of the given blueprint at this facility

        :param names: the name(s) of the target blueprint(s)
        :type names: ``str`` or ``list`` of ``str``

        You can use the following setting to prevent plumbery from stopping a
        node::

          - sql:
              domain: *vdc1
              ethernet: *data
              nodes:
                - slaveSQL:
                    running: always

        """

        nodes = PlumberyNodes(self)

        for name in self.expand_blueprint(names):

            blueprint = self.get_blueprint(name)

            if 'nodes' not in blueprint:
                continue

            nodes.stop_blueprint(blueprint)


class PlumberyFittings:
    """
    Describe fittings plan for one facility

    :param entries: plan of the fittings
    :type entries: ``dict``

    """

    def __init__(self, **entries):

        self.basement = None
        self.blueprints = []
        self.locationID = None
        self.regionID = None
        self.rub = []

        self.__dict__.update(entries)

    def __repr__(self):

        labels = []
        for item in self.blueprints:
            labels.append(item.keys()[0])

        return "<PlumberyFittings locationId: {}, regionId: {}, "   \
               "blueprints: {}, basement: {} >"    \
               .format(self.locationId, self.regionId,
                       ' '.join(labels), self.basement)
