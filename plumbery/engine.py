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

"""Are you looking for a cloud plumber? We hope this one will be useful to you
"""

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
    """Cloud automation at Dimension Data with Apache Libcloud"""

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
        """Build all blueprints"""

        print "Building all blueprints"

        for facility in self.facilities:
            facility.focus()
            facility.build_all_blueprints()

    def build_blueprint(self, name):
        """Build a named blueprint"""

        print "Building blueprint '{}'".format(name)

        for facility in self.facilities:
            facility.focus()
            facility.build_blueprint(name)

    def destroy_all_nodes(self):
        """Destroy all nodes"""

        print "Destroying nodes from all blueprints"

        for facility in self.facilities:
            facility.focus()
            facility.destroy_all_nodes()

    def destroy_nodes(self, name):
        """Destroy nodes"""

        print "Destroying nodes from blueprint '{}'".format(name)

        for facility in self.facilities:
            facility.focus()
            facility.destroy_nodes(name)

    def parse_layout(self, fileName=None):
        """Read description of the fittings"""

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
        """Start all nodes"""

        print "Starting nodes from all blueprints"

        for facility in self.facilities:
            facility.focus()
            facility.start_all_nodes()

    def start_nodes(self, name):
        """Start nodes"""

        print "Starting nodes from blueprint '{}'".format(name)

        for facility in self.facilities:
            facility.focus()
            facility.start_nodes(name)

    def stop_all_nodes(self):
        """Stop all nodes"""

        print "Stopping nodes from all blueprints"

        for facility in self.facilities:
            facility.focus()
            facility.stop_all_nodes()

    def stop_nodes(self, name):
        """Stop nodes"""

        print "Stopping nodes from blueprint '{}'".format(name)

        for facility in self.facilities:
            facility.focus()
            facility.stop_nodes(name)


class PlumberyBlueprints:
    """Describe how fittings should look at one facility"""

    # turn a dictionary to an object
    def __init__(self, **entries):
        self.__dict__.update(entries)
