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

from __future__ import absolute_import
import copy
import socket
import os

from plumbery.action import PlumberyActionLoader
from plumbery.exception import PlumberyException
from plumbery.infrastructure import PlumberyInfrastructure
from plumbery.plogging import plogging
from plumbery.nodes import PlumberyNodes
from plumbery.polisher import PlumberyPolisher

__all__ = ['PlumberyFacility']


class PlumberyFacility(object):
    """
    Plumbing at one facility

    :param plumbery: the automate that is coordinating
            plumbing activities at multiple facilities
    :type plumbery: :class:`plumbery.PlumberyEngine`

    :param fittings:  the plan for the fittings
    :type fittings: ``dict``

    Example::

        from plumbery.facility import PlumberyFacility
        facility = PlumberyFacility(plumbery=plumbery, fittings=fittings)
        facility.build_all_blueprints()

    In this example a facility is ruled by the given plumber, and the plan
    of all the fittings is provided as well.

    Attributes:

        plumbery:
            global settings and functions

        fittings:
            the plan is available when needed

    """

    def __init__(self, plumbery=None, fittings={}):
        """Puts this facility in context"""

        self.plumbery = plumbery

        self.facts = {}

        self.settings = {}

        self.blueprints = []

        for key in fittings.keys():

            if key == 'blueprints':
                self.blueprints = fittings['blueprints']

            else:
                self.settings[key] = fittings[key]

        self.finalize_settings()
        self.finalize_blueprints()

        # first call to the API is done in self.power_on()
        self.region = None
        self.location = None
        self.backup = None

        self._cache_images = []
        self._cache_network_domains = []
        self._cache_vlans = []

    def __repr__(self):

        return "<PlumberyFacility settings: {}>".format(self.settings)

    def finalize_settings(self):
        """
        Sets values for settings

        This function gets missing settings from default values set at
        the engine level.
        """

        mandatory = []
        for label in mandatory:
            if label not in self.settings:
                value = self.plumbery.get_default(label)
                if value is None:
                    raise ValueError("No value has been set for '{}'"
                                     .format(label))
                self.settings[label] = value

        if 'regionId' not in self.settings and 'locationId' in self.settings:
            self.settings['regionId'] = self.get_region(
                self.settings['locationId'])

    def get_location_id(self):
        """
        Retrieves the id of the current location

        :return:  the id of the current location, e.g., 'EU7' or 'NA9'
        :rtype: ``str``

        """

        return self.get_setting('locationId')

    def get_region(self, locationId=None):
        """
        Retrieves the region for some location

        :param locationId: if not provided, use location of this facility
        :type locationId: ``str`` or None

        :return:  the region, e.g., 'dd-eu' or 'dd-ap', etc.
        :rtype: ``str`` or None

        This function helps to bind well-known data centres to their respective regions.

        For example::

            >>>facility.get_region(locationID='EU6')
            'dd-eu'

            >>>facility.get_region(locationID='XY7')
            None

        """

        regions = {
            'AF3': 'dd-af',
            'AP3': 'dd-ap',
            'AP4': 'dd-ap',
            'AP5': 'dd-ap',
            'AU9': 'dd-au',
            'AU10': 'dd-au',
            'AU11': 'dd-au',
            'CA2': 'dd-ca',
            'EU6': 'dd-eu',
            'EU7': 'dd-eu',
            'EU8': 'dd-eu',
            'NA9': 'dd-na',
            'NA12': 'dd-na',
        }

        if locationId is None:
            locationId = self.get_setting('locationId')

        if locationId not in regions.keys():
            return None

        return regions[locationId]

    def get_setting(self, label, default=None):
        """
        Retrieves some setting

        :param label: the name of the setting to be retrieved
        :type label: ``str``

        :param default: the default value to return

        :return: the value set in fittings plan, or `None`
        :rtype: ``str`` most often

        """

        if label in self.settings:
            return self.settings[label]

        return self.plumbery.get_default(label, default)

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

        basement = self.get_setting('basement')

        if basement is None:
            return []

        return self.expand_blueprint(basement)

    def finalize_blueprints(self):
        """
        Sets default values for blueprints

        This function expands blueprints defined for this facility with
        default settings and settings stored by the global engine.

        """

        for blueprintName in self.list_blueprints():

            blueprint = self.get_blueprint(blueprintName)

            shell = copy.deepcopy(self.plumbery.get_default('domain', {}))
            if 'domain' in blueprint:
                self.update_settings(shell, blueprint['domain'])
            blueprint['domain'] = shell

            shell = copy.deepcopy(self.plumbery.get_default('ethernet', {}))
            if 'ethernet' in blueprint:
                self.update_settings(shell, blueprint['ethernet'])
            blueprint['ethernet'] = shell

            if 'nodes' in blueprint:

                for index in range(0, len(blueprint['nodes'])):

                    config = copy.deepcopy(self.plumbery.get_default(
                        'cloud-config', {}))

                    if not isinstance(blueprint['nodes'][index], dict):
                        raise TypeError('{} should be a dictionary'
                                        .format(blueprint['nodes'][index]))

                    label = list(blueprint['nodes'][index])[0]
                    settings = blueprint['nodes'][index][label]
                    if settings is None:
                        settings = {}

                    shell = {}
                    if 'default' in settings:
                        shell = copy.deepcopy(self.plumbery.get_default(
                            settings['default'], {}))
                        settings.pop('default')
                        if 'cloud-config' in shell:
                            self.update_settings(config, shell['cloud-config'])
                            shell.pop('cloud-config')

                    if 'cloud-config' in settings:
                        self.update_settings(config, settings['cloud-config'])
                        settings.pop('cloud-config')

                    self.update_settings(shell, settings)
                    settings = shell

                    if len(list(config)) > 0:
                        settings['cloud-config'] = config

                    blueprint['nodes'][index][label] = settings

            for index in range(0, len(self.blueprints)):
                if list(self.blueprints[index])[0] == blueprintName:
                    self.blueprints[index][blueprintName] = blueprint

    def update_settings(self, settings, additions):
        """
        Updates a dictionary deeply

        :param settings: the dictionary that will be updated
        :type settings: ``dict``

        :param additions: dictionary with some updates
        :type additions: ``dict``

        This function appends to any list in settings the elements
        provided in the dictionary additions.

        """

        if not isinstance(additions, dict):
            return

        for key in additions.keys():
            if additions[key] is None:
                pass

            elif key not in settings:
                settings[key] = additions[key]

            elif isinstance(settings[key], list):
                settings[key] += additions[key]

            elif isinstance(settings[key], dict):
                self.update_settings(settings[key], additions[key])

            else:
                settings[key] = additions[key]

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
        for blueprint in self.blueprints:
            name = list(blueprint)[0]
            if not isinstance(blueprint[name], dict):
                continue

            if name in names:
                raise ValueError("Duplicated blueprint name '{}'".format(name))

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
            defaults:
              blueprints: mongo_config mongo_shard

            ---

            basement: control admin

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

        If the special label `*` is provided, then plumbery will look
        for a default list of blueprints defined at the global level.
        Alternatively, it will provide the full list of blueprints.
        With the example settings above, you would get::

            >>facility.expand_blueprint('*')
            ['mongo_config', 'mongo_shard']

        If the special label `basement` is provided, then as you can expect
        it will be expanded as specified in the fittings plan. With the example
        settings above, you would get::

            >>facility.expand_blueprint('basement')
            ['control', 'admin']

        """

        names = []

        if isinstance(labels, str):

            if labels.lower() == '*':
                all = self.list_blueprints()
                labels = self.plumbery.get_default('blueprints', all)

            elif labels.lower() == 'basement':
                labels = self.get_setting('basement')

            if isinstance(labels, str):
                labels = labels.split(' ')

        for label in labels:

            for blueprint in self.blueprints:

                name = list(blueprint)[0]
                if name != label:
                    continue

                if isinstance(blueprint[name], dict):
                    if label not in names:
                        names.append(label)
                else:
                    for token in str(blueprint[name]).split(' '):
                        if token in names:
                            continue

                        for scanning in self.blueprints:
                            if token == list(scanning)[0]:
                                names.append(token)
                                break

        if names != labels:
            if len(names) > 1:
                plogging.info("- working on blueprints '{}'".format(
                    "', '".join(names)))
            elif len(names) > 0:
                plogging.info("- working on blueprint '{}'".format(
                    "', '".join(names)))
            else:
                plogging.info("- skipped - nothing to do here")

        return names

    def get_blueprint(self, name):
        """
        Retrieves a blueprint by name

        :param name: the name of the target blueprint
        :type name: ``str``

        :return: the blueprint with this name
        :rtype: ``dict`` or ``None``

        """

        for blueprint in self.blueprints:
            if name == list(blueprint)[0]:

                if not isinstance(blueprint[name], dict):
                    return None

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

        for blueprint in self.blueprints:
            name = list(blueprint)[0]
            if 'domain' in blueprint[name]:
                labels.add(blueprint[name]['domain']['name'])

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

        for blueprint in self.blueprints:
            name = list(blueprint)[0]
            if 'ethernet' in blueprint[name]:
                labels.add(blueprint[name]['ethernet']['name'])

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

        for blueprint in self.blueprints:
            name = list(blueprint)[0]
            if 'nodes' in blueprint[name]:
                for item in blueprint[name]['nodes']:
                    if type(item) is dict:
                        label = list(item)[0]

                    else:
                        label = item

                    for label in PlumberyNodes.expand_labels(label):
                        if label in labels:
                            plogging.warning("Duplicate node name '{}'"
                                             .format(label))
                        else:
                            labels.append(label)

        return labels

    def get_image(self, name=None):
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

            self._cache_images += \
                self.region.ex_list_customer_images(location=self.location)

        if (name is None and len(self._cache_images) > 0):
            return self._cache_images[0]

        for image in self._cache_images:
            if name in image.name:
                return image

        return None

    def focus(self):
        """
        Where are we plumbing?

        """

        self.power_on()
        plogging.info("Plumbing at '{}' {} ({})".format(
            self.location.id,
            self.location.name,
            self.location.country))

        blueprints = self.list_blueprints()
        if len(blueprints) < 1:
            plogging.warning("- no blueprint has been found")
        else:
            plogging.debug("- available blueprints: {}".format(
                "'"+"', '".join(blueprints)+"'"))

        basement = self.list_basement()
        if len(basement) > 0:
            plogging.debug("- basement: {}".format(
                "'"+"', '".join(basement)+"'"))

    def power_on(self):
        """
        Switches electricity on

        """

        regionId = self.get_setting('regionId')
        host = self.get_setting('apiHost')
        locationId = self.get_setting('locationId')

        try:

            if self.region is None:
                plogging.debug("Getting driver for '%s / %s'", regionId, host)
                self.region = self.plumbery.get_compute_driver(
                    region=regionId,
                    host=host)
                self.backup = self.plumbery.get_backup_driver(
                    region=regionId,
                    host=host)

                if os.getenv('LIBCLOUD_HTTP_PROXY') is not None:
                    plogging.debug('Setting proxy to %s' %
                                  (os.getenv('LIBCLOUD_HTTP_PROXY')))
                    self.region.connection.set_http_proxy(
                        proxy_url=os.getenv('LIBCLOUD_HTTP_PROXY'))
                    self.backup.connection.set_http_proxy(
                        proxy_url=os.getenv('LIBCLOUD_HTTP_PROXY'))
                    plogging.debug('Disabling SSL verification')
                    import libcloud.security
                    libcloud.security.VERIFY_SSL_CERT = False

            if self.location is None:
                plogging.debug("Getting location '{}'".format(locationId))
                locations = []
                for location in self.region.list_locations():
                    locations.append(location.id)
                    if location.id == locationId:
                        self.location = location

                if self.location is None:
                    plogging.info("Known locations: {}".format(locations))
                    raise PlumberyException("Unknown location '{}' in '{}'"
                                            .format(locationId, regionId))

        except ValueError:
            raise PlumberyException("Unknown region '{}'"
                                    .format(regionId))

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

        blueprints = self.expand_blueprint('*')
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

    def process_all_blueprints(self, action):
        """
        Handles all blueprints at this facility

        :param action: the action to perform, e.g., 'start'
        :type action: ``str`` or :class:`plumbery.PlumberyAction`

        """

        if isinstance(action, str):
            action = PlumberyActionLoader.from_shelf(action)

        self.power_on()
        action.enter(self)

        basement = self.list_basement()
        for name in basement:
            blueprint = self.get_blueprint(name)
            action.handle(blueprint)

        for name in self.expand_blueprint('*'):
            if name not in basement:
                blueprint = self.get_blueprint(name)
                action.handle(blueprint)

        action.quit()

    def process_blueprint(self, action, names):
        """
        Handles one blueprint at this facility

        :param action: the action to perform, e.g., 'start'
        :type action: ``str`` or :class:`plumbery.PlumberyAction`

        :param names: the name(s) of the targeted blueprint(s)
        :type names: ``str`` or ``list`` of ``str``

        """

        if isinstance(action, str):
            action = PlumberyActionLoader.from_shelf(action)

        self.power_on()
        action.enter(self)

        for name in self.expand_blueprint(names):

            blueprint = self.get_blueprint(name)
            action.handle(blueprint)

        action.quit()

    def start_all_blueprints(self):
        """
        Starts all nodes at this facility

        """

        basement = self.list_basement()
        for name in basement:
            self.start_blueprint(name)

        for name in self.expand_blueprint('*'):
            if name not in basement:
                self.start_blueprint(name)

    def start_blueprint(self, names):
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

    def polish_all_blueprints(self, polishers):
        """
        Walks all resources at this facility and polish them

        :param polishers: polishers to be applied
        :type polishers: list of :class:`plumbery.PlumberyPolisher`

        """

        basement = self.list_basement()
        for name in basement:
            plogging.debug("Polishing blueprint '{}'".format(name))
            self.polish_blueprint(name, polishers)

        for name in self.expand_blueprint('*'):
            if name not in basement:
                plogging.debug("Polishing blueprint '{}'".format(name))
                self.polish_blueprint(name, polishers)

    def polish_blueprint(self, names, polishers):
        """
        Walks a named blueprint for this facility and polish related resources

        :param names: the name(s) of the blueprint(s) to polish
        :type names: ``str`` or ``list`` of ``str``

        :param polishers: polishers to be applied
        :type polishers: list of :class:`plumbery.PlumberyPolisher`

        """

        if isinstance(polishers, str):
            polishers = PlumberyPolisher.filter(self.plumbery.polishers,
                                                polishers)

        self.power_on()
        infrastructure = PlumberyInfrastructure(self)
        nodes = PlumberyNodes(self)

        for polisher in polishers:
            polisher.move_to(self)

        for name in self.expand_blueprint(names):

            blueprint = self.get_blueprint(name)

            container = infrastructure.get_container(blueprint)

            for polisher in polishers:
                polisher.shine_container(container)

            nodes.polish_blueprint(blueprint, polishers, container)

    def stop_all_blueprints(self):
        """
        Stops all nodes at this facility

        """

        basement = self.list_basement()

        for name in self.expand_blueprint('*'):
            if name not in basement:
                self.stop_blueprint(name)

        for name in basement:
            self.stop_blueprint(name)

    def stop_blueprint(self, names):
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

    def wipe_all_blueprints(self):
        """
        Destroys all nodes at this facility

        """

        self.power_on()
        nodes = PlumberyNodes(self)

        basement = self.list_basement()

        for name in self.expand_blueprint('*'):
            if name in basement:
                continue
            blueprint = self.get_blueprint(name)
            plogging.debug("Wiping blueprint '{}'".format(name))
            nodes.destroy_blueprint(blueprint)

        for name in basement:
            blueprint = self.get_blueprint(name)
            plogging.debug("Wiping blueprint '{}'".format(name))
            nodes.destroy_blueprint(blueprint)

    def wipe_blueprint(self, names):
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

    def destroy_all_blueprints(self):
        """
        Destroys all blueprints at this facility

        """

        self.power_on()
        nodes = PlumberyNodes(self)
        infrastructure = PlumberyInfrastructure(self)

        basement = self.list_basement()

        for name in self.expand_blueprint('*'):
            if name in basement:
                continue
            blueprint = self.get_blueprint(name)
            plogging.debug("Destroying blueprint '{}'".format(name))
            nodes.destroy_blueprint(blueprint)
            infrastructure.destroy_blueprint(blueprint)

        for name in basement:
            blueprint = self.get_blueprint(name)
            plogging.debug("Destroying blueprint '{}'".format(name))
            nodes.destroy_blueprint(blueprint)
            infrastructure.destroy_blueprint(blueprint)

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

    def lookup(self, token):
        """
        Retrieves the value attached to a token

        :param token: the token, e.g., 'server1.ipv6'
        :type token: ``str``

        :return: the value attached to this token, or `None`

        """

        if token == 'location.country':
            return self.location.country

        if token == 'location.id':
            return self.get_location_id()

        if token in self.facts:
            return self.facts[token]

        return self.plumbery.lookup(token)

    def remember(self, token, value):
        """
        Remembers the value attached to a token

        :param token: the token, e.g., 'server1.private'
        :type token: ``str``

        :param value: the value attached to this token, e.g., '10.0.0.8'
        :type value: ``str``

        """

        self.facts[token] = value
