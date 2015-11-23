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
import os

# yaml for descriptions - http://pyyaml.org/wiki/PyYAMLDocumentation
import yaml

# Apache Libcloud - https://libcloud.readthedocs.org/en/latest
from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider

# other code related to plumbery
from facility import PlumberyFacility


__all__ = ['PlumberyEngine', 'PlumberyBlueprints']


class PlumberyEngine:
    """Cloud automation at Dimension Data with Apache Libcloud

    Plumbery is a convenient tool for infrastructure managers at cloud times.
    It allows for easy and repeatable deployments of various
    fittings, including compute nodes and related storage. It allows also for
    quick dismandling of the fittings when required.
    The idea here is not to compete with respected solutions such as chef or
    puppet. At its name implies, plumbery is targeting pipes and fittings, the
    very basic utility stuff that sophisticated tools can leverage.

    Args:
        fileName (str): the location of the plan for the fittings

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
    plan but from the environement as well.

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
        driver (libcloud.base.NodeDriver):
            A handle to the underlying Apache Libcloud instance

        facilities (list of PlumberyFacility objects):
            Breakdown of the overall plan over multiple facilities. This global
            attribute results from the parsing of the fittings plan.

        safeMode (boolean):
            If True, which is the default, then no actual change
            will be made against the infrastructure. This global attribute
            is coming from the fittings plan.

        sharedSecret (str):
            The main password used during the creation of a new
            node. This attribute is read from the local environment.

    """

    # the Apache Libcloud driver
    driver = None

    # the various facilities where fittings are put under control
    facilities = []

    # in safe mode no change is made to the fittings
    safeMode = True

    # the password to access remote servers
    sharedSecret = None

    def __init__(self, fileName=None):
        """Ignite the plumbering engine"""

        # get libcloud driver for Managed Cloud Platform (MCP) of Dimension Data
        self.driver = get_driver(Provider.DIMENSIONDATA)

        # get API credentials from environment - with bash, edit ~/.bash_profile to export your credentials in local environment
        self.userName = os.getenv('MCP_USERNAME', "Set environment variable MCP_USERNAME with credentials given to you")
        self.userPassword = os.getenv('MCP_PASSWORD', "Set environment variable MCP_PASSWORD with credentials given to you")

        # get root password from environment - with bash, edit ~/.bash_profile to export SHARED_SECRET in local environment
        self.sharedSecret = os.getenv('SHARED_SECRET')
        if self.sharedSecret is None or len(self.sharedSecret) < 3:
            print "Error: set environment variable SHARED_SECRET with the password to access nodes remotely!"
            exit(-1)

        # load the plan
        if fileName:
            self.parse_layout(fileName)

    def build_all_blueprints(self):
        """Build all blueprints

        This function will check all facilities, one at a time and in the order
        defined in fittings plan, to build all blueprints there.

        Example::

            from plumbery.engine import PlumberyEngine
            PlumberyEngine('fittings.yaml').build_all_blueprints()

        """

        print "Building all blueprints"

        for facility in self.facilities:
            facility.focus()
            facility.build_all_blueprints()

    def build_blueprint(self, name):
        """Build a named blueprint

        This function will check all facilities, one at a time and in the order
        defined in fittings plan, to build one single blueprint there.

        Args:
            name (str): the name of the blueprint to deploy

        Example::

            from plumbery.engine import PlumberyEngine
            PlumberyEngine('fittings.yaml').build_blueprints('sql')

        """

        print "Building blueprint '{}'".format(name)

        for facility in self.facilities:
            facility.focus()
            facility.build_blueprint(name)

    def destroy_all_nodes(self):
        """Destroy all nodes

        This function will check all facilities, one at a time and in the order
        defined in fittings plan, to destroy all nodes there.

        Note:
            Running nodes are always preserved from destruction.
            Therefore the need to stop nodes, in a separate command, before
            they can be actually destroyed.

        """

        print "Destroying nodes from all blueprints"

        for facility in self.facilities:
            facility.focus()
            facility.destroy_all_nodes()

    def destroy_nodes(self, name):
        """Destroy nodes

        This function will check all facilities, one at a time and in the order
        defined in fittings plan, to destroy nodes from one single blueprint.

        Args:
            name (str): the name of the blueprint to destroy

        Note:
            Running nodes are always preserved from destruction.
            Therefore the need to stop nodes, in a separate command, before
            they can be actually destroyed.

        """

        print "Destroying nodes from blueprint '{}'".format(name)

        for facility in self.facilities:
            facility.focus()
            facility.destroy_nodes(name)

    def parse_layout(self, fileName=None):
        """Read the fittings plan

        The fittings plan is expected to follow YAML specifications, and its
        structure has to follow some rules described here.

        Args:
            fileName (str): the location of the plan for the fittings

        An example of a minimum fittings plan::

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
                    - myServer:

        In this example, the plan is to deploy a single node in the data centre
        at Frankfurt, in Europe. The node `myServer` will be placed in a
        network named `myVLAN`, and the network will be part of a network
        domain acting as a virtual data centre, `myDC`. The blueprint has a
        name, `myBluePrint`, so that it can be handled independently from
        other blueprints.
        """

        # get file name from the environment, or use default name
        if not fileName:
            fileName = os.getenv('PLUMBERY', 'fittings.yaml')

        # maybe file cannot be read or YAML is broken
        try:
            with open(fileName, 'r') as stream:
                documents = yaml.load_all(stream)

                # first document provides meta information
                document = documents.next()

                if 'safeMode' in document:
                    self.safeMode = document['safeMode']

                # one document per facility
                for document in documents:
                    facility = PlumberyFacility(self, PlumberyBlueprints(**document))
                    self.facilities.append(facility)

        except Exception as feedback:
            print "Error: unable to load file '{}'!".format(fileName)
            print feedback
            exit(-1)

        # are we in safe mode?
        if self.safeMode:
            print "Running in safe mode - no actual change will be made to the fittings"

    def start_all_nodes(self):
        """Start all nodes

        This function will check all facilities, one at a time and in the order
        defined in fittings plan, to start all nodes there.

        This function has no effect on nodes that are already up and running.

        """

        print "Starting nodes from all blueprints"

        for facility in self.facilities:
            facility.focus()
            facility.start_all_nodes()

    def start_nodes(self, name):
        """Start nodes

        This function will check all facilities, one at a time and in the order
        defined in fittings plan, to start nodes from one single blueprint.

        Args:
            name (str): the name of the blueprint to start

        This function has no effect on nodes that are already up and running.

        """

        print "Starting nodes from blueprint '{}'".format(name)

        for facility in self.facilities:
            facility.focus()
            facility.start_nodes(name)

    def stop_all_nodes(self):
        """Stop all nodes

        This function will check all facilities, one at a time and in the order
        defined in fittings plan, to stop all nodes there.

        This function has no effect on nodes that are already stopped.

        """

        print "Stopping nodes from all blueprints"

        for facility in self.facilities:
            facility.focus()
            facility.stop_all_nodes()

    def stop_nodes(self, name):
        """Stop nodes

        This function will check all facilities, one at a time and in the order
        defined in fittings plan, to stop nodes from one single blueprint.

        Args:
            name (str): the name of the blueprint to stop

        This function has no effect on nodes that are already stopped.

        """

        print "Stopping nodes from blueprint '{}'".format(name)

        for facility in self.facilities:
            facility.focus()
            facility.stop_nodes(name)


class PlumberyBlueprints:
    """Describe fittings plan for one facility"""

    # turn a dictionary to an object
    def __init__(self, **entries):
        self.__dict__.update(entries)
