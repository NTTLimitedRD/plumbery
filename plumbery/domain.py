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
from exceptions import PlumberyException

__all__ = ['PlumberyDomain']


class PlumberyDomain:
    """Cloud automation for a network domain

    A network domain is similar to a virtual data center. It is a secured
    container for multiple nodes.

    Args:
        facility (PlumberyFacility): the underlying physical facility

    Example::

        from plumbery.domain import PlumberyDomain
        domain = PlumberyDomain(facility=facility)
        domain.build_blueprint(blueprint=blueprint)

    In this example a domain is initialised at the given facility, and then
    it is asked to create the pipes and the plumbery mentioned in the
    provided blueprint. This is covering solely the network and the security,
    not the nodes themselves.

    Attributes:
        facility (PlumberyFacility): a handle to the physical facility where
            network domains are implemented

    """

    # the physical data center
    facility = None

    def __init__(self, facility=None, logger=None):
        """Put network domains in context"""

        # handle to parent parameters and functions
        self.facility = facility
        self.region = facility.region
        self.plumbery = facility.plumbery
        self.logger = logger if logger is not None else print
        self.network = None
        self.domain = None

    def build(self, blueprint):
        """Create network domain if it does not exist

        Args:
            blueprint (dict): the various attributes of the target fittings

        """

        # check the target network domain
        if 'domain' not in blueprint or type(blueprint['domain']) is not dict:
            raise PlumberyException("Error: no network domain has been defined for the blueprint '{}'!".format(blueprint['target']))

        # seek for an existing network domain with this name
        domainName = blueprint['domain']['name']
        self.domain = None
        for self.domain in self.region.ex_list_network_domains(location=self.facility.location):
            if self.domain.name == domainName:
                self.logger("Network domain '{}' already exists".format(domainName))
                break

        # create a network domain if needed
        if self.domain is None or self.domain.name != domainName:

            if self.plumbery.safeMode:
                self.logger("Would have created network domain '{}' if not in safe mode".format(domainName))
                exit(0)

            else:
                self.logger("Creating network domain '{}'".format(domainName))

                # the description attribute is a smart way to tag resources
                description = '#plumbery'
                if 'description' in blueprint['domain']:
                    description = blueprint['domain']['description'] + ' #plumbery'

                # level of service
                service = 'ESSENTIALS'
                if 'service' in blueprint['domain']:
                    service = blueprint['domain']['service']

                try:
                    self.domain = self.region.ex_create_network_domain(
                        location=self.facility.location,
                        name=domainName,
                        service_plan=service,
                        description=description)
                    self.logger("- in progress")
                    self.region.ex_wait_for_state(
                        'NORMAL', self.region.ex_get_network_domain,
                        poll_interval=2, timeout=1200,
                        network_domain_id=self.domain.id)

                except Exception as feedback:
                    raise PlumberyException(
                        "Error: unable to create network domain '{1}' {2]!".format(domainName, feedback))

        # check name of the target network
        if 'ethernet' not in blueprint or type(blueprint['ethernet']) is not dict:
            raise PlumberyException(
                "Error: no ethernet network has been defined for the blueprint '{}'!".format(blueprint['target']))

        # check addresses to use for the target network
        if 'subnet' not in blueprint['ethernet']:
            raise PlumberyException("Error: no IPv4 subnet (e.g., '10.0.34.0') as been defined for the blueprint '{}'!".format(blueprint['target']))

        # seek for an existing network with this name
        networkName = blueprint['ethernet']['name']
        self.network = None
        for self.network in self.region.ex_list_vlans(location=self.facility.location, network_domain=self.domain):
            if self.network.name == networkName:
                self.logger("Ethernet network '{}' already exists".format(networkName))
                break

        # create a network if needed
        if self.network is None or self.network.name != networkName:

            if self.plumbery.safeMode:
                self.logger("Would have created Ethernet network '{}' if not in safe mode".format(networkName))
                exit(0)

            else:
                self.logger("Creating Ethernet network '{}'".format(networkName))

                # the description attribute is a smart way to tag resources
                description = '#plumbery'
                if 'description' in blueprint['ethernet']:
                    description = blueprint['ethernet']['description'] + ' #plumbery'

                try:
                    self.network = self.region.ex_create_vlan(
                        network_domain=self.domain,
                        name=networkName,
                        private_ipv4_base_address=blueprint['ethernet']['subnet'],
                        description=description)
                    self.logger("- in progress")
                    # Wait for the VLAN to be provisioned
                    self.region.ex_wait_for_state('NORMAL', self.region.ex_get_vlan,
                             poll_interval=2, timeout=1200,
                             vlan_id=self.network.id)

                except Exception as feedback:
                    raise PlumberyException("Error: unable to create Ethernet network '{1}' {2}!".format(networkName, feedback))
