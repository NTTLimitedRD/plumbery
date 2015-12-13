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
import os
import yaml

from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider

from exceptions import PlumberyException
from facility import PlumberyFacility
from polisher import PlumberyPolisher

__all__ = ['PlumberyEngine', 'PlumberyFittings']


class PlumberyEngine:
    """
    Cloud automation at Dimension Data with Apache Libcloud

    :param fileName: the location of the plan for the fittings
    :type fileName: ``str``

    Plumbery is a convenient tool for infrastructure managers at cloud times.
    It allows for easy and repeatable deployments of various
    fittings, including compute nodes and related storage. It allows also for
    quick dismandling of the fittings when required.
    The idea here is not to compete with respected solutions such as chef or
    puppet. At its name implies, plumbery is targeting pipes and fittings, the
    very basic utility stuff that sophisticated tools can leverage.

    Example::

        from plumbery.engine import PlumberyEngine
        engine = PlumberyEngine('fittings.yaml')
        engine.build_all_blueprints()

    In this example the overall plan, in textual format, is given to the engine
    in preparation of subsequent processing. The software is not trying to guess
    a name by default, so if you do not provide a name, no configuration file
    is loaded. You can load the plan at any stage, or restart the engine
    with an updated plan, by invoking the member function `parse_layout()`

    Note:
        While plumbery is not making assumptions for your configuration files,
        if your infrastructure is simple enough to fit in one single file then
        you are highly encouraged to name it `fittings.yaml`

    Beyond the plan for your fittings, plumbery is also requiring some specific
    credentials to connect to cloud providers. To preserve the confidentiality
    of such information, it is read from the environment, and not from any
    configuration file. Therefore the need for local setup before running
    plumbery. This is part of the installation process.

    Last but not least, plumbery sets the root password of any new server that
    it creates. For obvious security reasons this is not taken from the fittings
    plan but from the environment, or it can be set in code.

    Under Linux, you may want to edit `~/.bash_profile` like this::

        # credentials to access cloud resources from Dimension Data
        export MCP_USERNAME='foo.bar'
        export MCP_PASSWORD='WhatsUpDoc'

        # password to access nodes remotely
        export SHARED_SECRET='*you really want to put a tricky password here*'

    These simple precautions are aiming to protect your infrastructure as much
    as possible. The general goal is to minimize risks induced by exposure to
    your fittings plan. You may lead transformation towards so-called
    infrastructure as code, and for this you will add version control to your
    fittings plan. As a result, plans will be stored in git or equivalent, and
    shared across some people.

    Attributes:
        provider (libcloud.base.NodeDriver):
            A handle to the underlying Apache Libcloud instance

        facilities (list of PlumberyFacility objects):
            Breakdown of the overall plan over multiple facilities. This global
            attribute results from the parsing of the fittings plan.

        safeMode (boolean):
            If True, which is the default, then no actual change
            will be made against the infrastructure. This global attribute
            is coming from the fittings plan.

    """

    facilities = []

    polishers = []

    provider = None

    safeMode = True

    _sharedSecret = None

    _userName = None

    _userPassword = None

    def __init__(self, fileName=None):
        """
        Ignites the plumbing engine

        :param   fileName: The file path of the blueprints
        :type    fileName: ``str``

        """

        self.provider = self.get_provider()

        if fileName:
            self.setup(fileName)

    def add_facility(self, facility):
        """
        Extends the scope of this plumbing engine

        :param facility: description of an additional facility
        :type facility: ``dict`` or class:`plumbery.PlumberyFacility`

        """

        if isinstance(facility, dict):
            facility = PlumberyFacility(self, PlumberyFittings(**facility))

        self.facilities.append(facility)

    def build_all_blueprints(self):
        """
        Builds all blueprints described in fittings plan

        This function checks all facilities, one at a time and in the order
        defined in fittings plan, to build all blueprints there.

        Example::

            from plumbery.engine import PlumberyEngine
            PlumberyEngine('fittings.yaml').build_all_blueprints()

        """

        logging.info("Building all blueprints")

        for facility in self.facilities:
            facility.focus()
            facility.build_all_blueprints()

        self.polish_all_blueprints(filter=self._buildPolisher)

    def build_blueprint(self, name):
        """
        Builds a named blueprint from fittings plan

        :param name: the name of the blueprint to deploy
        :type name: ``str``

        This function checks all facilities, one at a time and in the order
        defined in fittings plan, to build one single blueprint there.

        Example::

            from plumbery.engine import PlumberyEngine
            PlumberyEngine('fittings.yaml').build_blueprints('sql')

        """

        logging.info("Building blueprint '{}'".format(name))

        for facility in self.facilities:
            facility.focus()
            facility.build_blueprint(name)

        self.polish_blueprint(name=name, filter=self._buildPolisher)

    def configure(self, settings):
        """
        Changes running settings of the engine

        :param settings: the new settings
        :type settings: ``dict``

        """

        if not isinstance(settings, dict):
            raise TypeError('settings should be a dictionary')

        if 'safeMode' not in settings:
            raise LookupError('safeMode is not defined')

        self.safeMode = settings['safeMode']
        if self.safeMode not in [True, False]:
            raise ValueError('safeMode should be either True or False')

        if 'polishers' in settings:
            for item in settings['polishers']:
                key = item.keys()[0]
                value = item[key]
                self.polishers.append(
                    PlumberyPolisher.from_shelf(key, value))

        if 'buildPolisher' in settings:
            self._buildPolisher = settings['buildPolisher']
        else:
            self._buildPolisher = 'spit'

    def destroy_all_blueprints(self):
        """
        Destroys all blueprints from fittings plan

        This function checks all facilities, one at a time and in the order
        defined in fittings plan, to destroy all blueprints there.

        Note:
            Running nodes are always preserved from destruction.
            Therefore the need to stop nodes, in a separate command, before
            they can be actually destroyed.

        """

        logging.info("Destroying all blueprints")

        for facility in self.facilities:
            facility.focus()
            facility.destroy_all_blueprints()

    def destroy_all_nodes(self):
        """
        Destroys all nodes from fittings plan

        This function checks all facilities, one at a time and in the order
        defined in fittings plan, to destroy all nodes there.

        Note:
            Running nodes are always preserved from destruction.
            Therefore the need to stop nodes, in a separate command, before
            they can be actually destroyed.

        """

        logging.info("Destroying nodes from all blueprints")

        for facility in self.facilities:
            facility.focus()
            facility.destroy_all_nodes()

    def destroy_blueprint(self, name):
        """
        Destroys one blueprint from fittings plan

        :param name: the name of the blueprint to destroy
        :type name: ``str``

        This function checks all facilities, one at a time and in the order
        defined in fittings plan, to destroy one single blueprint.

        Note:
            Running nodes are always preserved from destruction.
            Therefore the need to stop nodes, in a separate command, before
            they can be actually destroyed.

        """

        logging.info("Destroying blueprint '{}'".format(name))

        for facility in self.facilities:
            facility.focus()
            facility.destroy_blueprint(name)

    def destroy_nodes(self, name):
        """
        Destroys nodes for one blueprint of the fittings plan

        :param name: the name of the blueprint to destroy
        :type name: ``str``

        This function checks all facilities, one at a time and in the order
        defined in fittings plan, to destroy nodes from one single blueprint.

        Note:
            Running nodes are always preserved from destruction.
            Therefore the need to stop nodes, in a separate command, before
            they can be actually destroyed.

        """

        logging.info("Destroying nodes from blueprint '{}'".format(name))

        for facility in self.facilities:
            facility.focus()
            facility.destroy_nodes(name)

    def get_provider(self):
        """
        Loads a provider from Apache Libcloud

        This is the function to override if you want to use plumbery with
        any cloud service provider known by libcloud.

        """

        return get_driver(Provider.DIMENSIONDATA)

    def get_shared_secret(self):
        """
        Retrieves the secret that is communicated to new nodes during setup

        :returns: ``str``
            - the shared secret to be given to the driver

        :raises: :class:`plumbery.PlumberyException`
            - if no shared secret can be found

        The shared secret is not put in the fittings plan, but is normally taken
        from the environment variable ``SHARED_SECRET``.

        Under Linux, you may want to edit `~/.bash_profile` like this::

            # password to access nodes remotely
            export SHARED_SECRET='*you really want to use a tricky password*'

        Alternatively, you can use the member function ``set_shared_secret`` to
        set this important attribute via code.

        """

        if not self._sharedSecret:
            self._sharedSecret = os.getenv('SHARED_SECRET')
            if self._sharedSecret is None or len(self._sharedSecret) < 3:
                raise PlumberyException(
                    "Error: missing node password in environment SHARED_SECRET")

        return self._sharedSecret

    def get_user_name(self):
        """
        Retrieves user name to authenticate to the API

        :returns: ``str``
            - the user name to be used with the driver
        :raises: :class:`plumbery.PlumberyException`
            - if no user name can be found

        The user name is not put in the fittings plan, but is normally taken
        from the environment variable ``MCP_USERNAME``.

        Under Linux, you may want to edit `~/.bash_profile` like this::

            # credentials to access cloud resources from Dimension Data
            export MCP_USERNAME='foo.bar'
            export MCP_PASSWORD='WhatsUpDoc'

        """

        if not self._userName:
            self._userName = os.getenv('MCP_USERNAME')
            if self._userName is None or len(self._userName) < 3:
                raise PlumberyException(
                    "Error: missing credentials in environment MCP_USERNAME")

        return self._userName

    def get_user_password(self):
        """
        Retrieves user password to authenticate to the API

        :returns: ``str``
            - the user password to be used with the driver
        :raises: :class:`plumbery.PlumberyException`
            - if no user password can be found

        The user password is not put in the fittings plan, but is normally taken
        from the environment variable ``MCP_PASSWORD``.

        Under Linux, you may want to edit `~/.bash_profile` like this::

            # credentials to access cloud resources from Dimension Data
            export MCP_USERNAME='foo.bar'
            export MCP_PASSWORD='WhatsUpDoc'

        """

        if not self._userPassword:
            self._userPassword = os.getenv('MCP_PASSWORD')
            if self._userPassword is None or len(self._userPassword) < 3:
                raise PlumberyException(
                    "Error: missing credentials in environment MCP_PASSWORD")

        return self._userPassword

    def polish_all_blueprints(self, filter=None):
        """
        Walks all resources and polishes them

        :param filter: the name of a single polisher to apply. If this
            parameter is missing, all polishers declared in the fittings plan
            will be applied
        :type filter: ``str``

        This function checks all facilities, one at a time and in the order
        defined in fittings plan, to apply custom polishers there.

        Example::

            from plumbery.engine import PlumberyEngine
            PlumberyEngine('fittings.yaml').polish_all_blueprints()

        """

        logging.info("Polishing all blueprints")

        polishers = PlumberyPolisher.filter(self.polishers, filter)

        for polisher in polishers:
            polisher.go(self)

        for facility in self.facilities:
            facility.focus()
            for polisher in polishers:
                polisher.move_to(facility)
            facility.polish_all_blueprints(polishers)

        for polisher in polishers:
            polisher.reap()

    def polish_blueprint(self, name, filter=None):
        """
        Walkes resources from the target blueprint and polishes them

        :param name: the name of the blueprint to polish
        :type name: ``str``

        :param filter: the name of a single polisher to apply. If this
            parameter is missing, all polishers declared in the fittings plan
            will be applied
        :type filter: ``str``

        This function checks all facilities, one at a time and in the order
        defined in fittings plan, to apply custom polishers there.

        Example::

            from plumbery.engine import PlumberyEngine
            PlumberyEngine('fittings.yaml').polish_blueprint('sql')

        """

        logging.info("Polishing blueprint '{}'".format(name))

        polishers = PlumberyPolisher.filter(self.polishers, filter)

        for polisher in polishers:
            polisher.go(self)

        for facility in self.facilities:
            facility.focus()
            for polisher in polishers:
                polisher.move_to(facility)
            facility.polish_blueprint(name, polishers)

        for polisher in polishers:
            polisher.reap()

    def set_shared_secret(self, secret):
        """
        Changes the shared secret to be used with new nodes

        :param secret: the user name to be used with the driver
        :type secret: ``str``

        This function can be used to supplement the normal provision of
        the shared secret via the environment variable ``SHARED_SECRET``.

        """

        self._sharedSecret = secret

    def set_user_name(self, name):
        """
        Changes the name used to authenticate to the API

        :param name: the user name to be used with the driver
        :type name: ``str``

        This function can be used to supplement the normal provision of
        a user name via the environment variable ``MCP_USERNAME``.

        """

        self._userName = name

    def set_user_password(self, password):
        """
        Changes the password used to authenticate to the API

        :param password: the user password to be used with the driver
        :type password: ``str``

        This function can be used to supplement the normal provision of
        a user password via the environment variable ``MCP_PASSWORD``.

        """

        self._userPassword = password

    def setup(self, plan=None):
        """
        Reads the fittings plan

        :param plan: the plan for the fittings
        :type plan: ``str`` or ``file`

        The fittings plan is expected to follow YAML specifications, and it
        must have multiple documents in it. The first document provides
        general configuration parameters for the engine. Subsequent documents
        describe the various locations for the fittings.

        An example of a minimum fittings plan::

            ---
            safeMode: False
            ---
            # Frankfurt in Europe
            locationId: EU6
            regionId: dd-eu

            blueprints:

              - myBluePrint:
                  domain:
                    name: myDC
                  ethernet:
                    name: myVLAN
                    subnet: 10.1.10.0
                  nodes:
                    - myServer

        In this example, the plan is to deploy a single node in the data centre
        at Frankfurt, in Europe. The node `myServer` will be placed in a
        network named `myVLAN`, and the network will be part of a network
        domain acting as a virtual data centre, `myDC`. The blueprint has a
        name, `myBluePrint`, so that it can be handled independently from
        other blueprints.
        """

        if plan is None:
            plan = os.getenv('PLUMBERY')

        if isinstance(plan, str):
            plan = open(plan, 'r')

        documents = yaml.load_all(plan)

        # first document contains engine settings
        self.configure(documents.next())

        # then one document per facility
        for document in documents:
            self.add_facility(document)

        if self.safeMode:
            logging.info("Running in safe mode"
                " - no actual change will be made to the fittings")

    def start_all_nodes(self):
        """
        Starts all nodes described in the fittings plan

        This function checks all facilities, one at a time and in the order
        defined in fittings plan, to start all nodes there.

        This function has no effect on nodes that are already up and running.

        """

        logging.info("Starting nodes from all blueprints")

        for facility in self.facilities:
            facility.focus()
            facility.start_all_nodes()

    def start_nodes(self, name):
        """
        Starts nodes of one blueprint of the fittings plan

        :param name: the name of the blueprint to start
        :type name: ``str``

        This function checks all facilities, one at a time and in the order
        defined in fittings plan, to start nodes from one single blueprint.

        This function has no effect on nodes that are already up and running.

        """

        logging.info("Starting nodes from blueprint '{}'".format(name))

        for facility in self.facilities:
            facility.focus()
            facility.start_nodes(name)

    def stop_all_nodes(self):
        """
        Stops all nodes of the fittings plan

        This function checks all facilities, one at a time and in the order
        defined in fittings plan, to stop all nodes there.

        This function has no effect on nodes that are already stopped.

        """

        logging.info("Stopping nodes from all blueprints")

        for facility in self.facilities:
            facility.focus()
            facility.stop_all_nodes()

    def stop_nodes(self, name):
        """
        Stops nodes of one blueprint of the fittings plan

        :param name: the name of the blueprint to stop
        :type name: ``str``

        This function checks all facilities, one at a time and in the order
        defined in fittings plan, to stop nodes from one single blueprint.

        This function has no effect on nodes that are already stopped.

        """

        logging.info("Stopping nodes from blueprint '{}'".format(name))

        for facility in self.facilities:
            facility.focus()
            facility.stop_nodes(name)


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

        return "<PlumberyFittings locationId: {}, regionId: {}, "       \
            "rub: {}, blueprints: {}, basement: {}>"                    \
            .format(self.locationId, self.regionId, self.rub,           \
                self.blueprints, self.basement)

