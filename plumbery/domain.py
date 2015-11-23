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

    def __init__(self, facility=None):
        """Put network domains in context"""

        # handle to parent parameters and functions
        self.facility = facility
        self.region = facility.region
        self.plumbery = facility.plumbery

    def build(self, blueprint):
        """Create network domain if it does not exist

        Args:
            blueprint (dict): the various attributes of the target fittings

        """

        # check the target network domain
        if 'domain' not in blueprint or type(blueprint['domain']) is not dict:
            print("Error: no network domain has been defined for the blueprint '{}'!".format(blueprint['target']))
            exit(-1)

        # seek for an existing network domain with this name
        domainName = blueprint['domain']['name']
        self.domain = None
        for self.domain in self.region.ex_list_network_domains(location=self.facility.location):
            if self.domain.name == domainName:
                print("Network domain '{}' already exists".format(domainName))
                break

        # create a network domain if needed
        if self.domain is None or self.domain.name != domainName:

            if self.plumbery.safeMode:
                print("Would have created network domain '{}' if not in safe mode".format(domainName))
                exit(0)

            else:
                print("Creating network domain '{}'".format(domainName))

                # the description attribute is a smart way to tag resources
                description = '#plumbery'
                if 'description' in blueprint['domain']:
                    description = blueprint['domain']['description'] + ' #plumbery'

                # level of service
                service = 'ESSENTIALS'
                if 'service' in blueprint['domain']:
                    service = blueprint['domain']['service']

                # we may have to wait for busy resources
                while True:

                    try:
                        self.domain = self.region.ex_create_network_domain(
                            location=self.facility.location,
                            name=domainName,
                            service_plan=service,
                            description=description)
                        print("- in progress")

                    except Exception as feedback:

                        # resource is busy, wait a bit and retry
                        if 'RESOURCE_BUSY' in str(feedback):
                            self.facility.wait_and_tick()
                            continue

                        # fatal error
                        else:
                            print("Error: unable to create network domain '{}'!".format(domainName))
                            print(str(feedback))
                            exit(-1)

                    # quit the loop
                    break

        # check name of the target network
        if 'ethernet' not in blueprint or type(blueprint['ethernet']) is not dict:
            print("Error: no ethernet network has been defined for the blueprint '{}'!".format(blueprint['target']))
            exit(-1)

        # check addresses to use for the target network
        if 'subnet' not in blueprint['ethernet']:
            print("Error: no IPv4 subnet (e.g., '10.0.34.0') as been defined for the blueprint '{}'!".format(blueprint['target']))
            exit(-1)

        # seek for an existing network with this name
        networkName = blueprint['ethernet']['name']
        self.network = None
        for self.network in self.region.ex_list_vlans(location=self.facility.location, network_domain=self.domain):
            if self.network.name == networkName:
                print("Ethernet network '{}' already exists".format(networkName))
                break

        # create a network if needed
        if self.network is None or self.network.name != networkName:

            if self.plumbery.safeMode:
                print("Would have created Ethernet network '{}' if not in safe mode".format(networkName))
                exit(0)

            else:
                print("Creating Ethernet network '{}'".format(networkName))

                # the description attribute is a smart way to tag resources
                description = '#plumbery'
                if 'description' in blueprint['ethernet']:
                    description = blueprint['ethernet']['description'] + ' #plumbery'

                # we may have to wait for busy resources
                while True:

                    try:
                        self.network = self.region.ex_create_vlan(
                            network_domain=self.domain,
                            name=networkName,
                            private_ipv4_base_address=blueprint['ethernet']['subnet'],
                            description=description)
                        print "- in progress"

                    except Exception as feedback:

                        # resource is busy, wait a bit and retry
                        if 'RESOURCE_BUSY' in str(feedback):
                            self.facility.wait_and_tick()
                            continue

                        # fatal error
                        else:
                            print("Error: unable to create Ethernet network '{}'!".format(networkName))
                            print(str(feedback))
                            exit(-1)

                    # quit the loop
                    break
