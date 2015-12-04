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

from exceptions import PlumberyException

__all__ = ['PlumberyDomain']


class PlumberyDomain:
    """
    Cloud automation for a network domain

    :param facility: the underlying physical facility
    :type facility: :class:`plumbery.PlumberFacility`

    A network domain is similar to a virtual data center. It is a secured
    container for multiple nodes.

    Example::

        from plumbery.domain import PlumberyDomain
        domain = PlumberyDomain(facility)
        domain.build(blueprint)

    In this example a domain is initialised at the given facility, and then
    it is asked to create the pipes and the plumbery mentioned in the
    provided blueprint. This is covering solely the network and the security,
    not the nodes themselves.

    Attributes:
        facility (PlumberyFacility):
            a handle to the physical facility where network domains
            are implemented

    """

    # the physical data center
    facility = None

    def __init__(self, facility=None):
        """Put network domains in context"""

        # handle to parent parameters and functions
        self.facility = facility
        self.region = facility.region
        self.plumbery = facility.plumbery
        self.network = None
        self.domain = None

    def build(self, blueprint):
        """
        Creates a network domain if needed.

        :param blueprint: the various attributes of the target fittings
        :type blueprint: ``dict``

        :returns: ``bool``
            - True if the network has been created or is already there,
            False otherwise
        :raises: :class:`plumbery.PlumberyException` if some unrecoverable error occurs

        This function is looking at all fittings in the blueprint except the
        nodes. This is including:

        * the network domain itself
        * one or multiple Ethernet networks

        In safe mode, the function will stop on any missing component since
        it is not in a position to add fittings, and return ``False``.
        If all components already exist then the funciton will return ``True``.

        """

        if 'domain' not in blueprint or type(blueprint['domain']) is not dict:
            raise PlumberyException(
                "Error: no network domain has been defined " \
                     "for the blueprint '{}'!".format(blueprint['target']))

        domainName = blueprint['domain']['name']
        self.domain = None
        for self.domain in self.region.ex_list_network_domains(
                                        location=self.facility.location):
            if self.domain.name == domainName:
                logging.info("Network domain '{}' already exists"
                                                        .format(domainName))
                break

        if self.domain is None or self.domain.name != domainName:

            if self.plumbery.safeMode:
                logging.info("Would have created network domain '{}' " \
                                    "if not in safe mode".format(domainName))
                return False

            else:
                logging.info("Creating network domain '{}'".format(domainName))

                # the description attribute is a smart way to tag resources
                description = '#plumbery'
                if 'description' in blueprint['domain']:
                    description = blueprint['domain']['description']+' #plumbery'

                # level of service
                service = 'ESSENTIALS'
                if 'service' in blueprint['domain']:
                    service = blueprint['domain']['service']

                while True:
                    try:
                        self.domain = self.region.ex_create_network_domain(
                            location=self.facility.location,
                            name=domainName,
                            service_plan=service,
                            description=description)
                        logging.info("- in progress")

                    except Exception as feedback:

                        if 'RESOURCE_BUSY' in str(feedback):
                            time.sleep(10)
                            continue

                        raise PlumberyException(
                            "Error: unable to create network domain '{0}' {1}!"
                                            .format(domainName, feedback))

                    break

        if 'ethernet' not in blueprint or type(blueprint['ethernet']) is not dict:
            raise PlumberyException(
                "Error: no ethernet network has been defined " \
                        "for the blueprint '{}'!".format(blueprint['target']))

        if 'subnet' not in blueprint['ethernet']:
            raise PlumberyException("Error: no IPv4 subnet " \
                "(e.g., '10.0.34.0') as been defined for the blueprint '{}'!"
                                                .format(blueprint['target']))

        networkName = blueprint['ethernet']['name']
        self.network = None
        for self.network in self.region.ex_list_vlans(
                                        location=self.facility.location,
                                        network_domain=self.domain):
            if self.network.name == networkName:
                logging.info("Ethernet network '{}' already exists"
                                                        .format(networkName))
                break

        if self.network is None or self.network.name != networkName:

            if self.plumbery.safeMode:
                logging.info("Would have created Ethernet network '{}' " \
                                    "if not in safe mode".format(networkName))
                return False

            else:
                logging.info("Creating Ethernet network '{}'"
                                                        .format(networkName))

                # the description attribute is a smart way to tag resources
                description = '#plumbery'
                if 'description' in blueprint['ethernet']:
                    description = blueprint['ethernet']['description']+' #plumbery'

                while True:
                    try:
                        self.network = self.region.ex_create_vlan(
                            network_domain=self.domain,
                            name=networkName,
                            private_ipv4_base_address=blueprint['ethernet']['subnet'],
                            description=description)
                        logging.info("- in progress")

                    except Exception as feedback:

                        if 'RESOURCE_BUSY' in str(feedback):
                            time.sleep(10)
                            continue

                        elif 'NAME_NOT_UNIQUE' in str(feedback):
                            logging.info("- network already exists")

                        else:
                            raise PlumberyException("Error: unable to create " \
                                            "Ethernet network '{0}' {1}!"
                                                .format(networkName, feedback))

                    break

        return True

    def destroy_blueprint(self, blueprint):
        """
        Destroys a domain attached to a blueprint

        :param blueprint: the various attributes of the target fittings
        :type blueprint: ``dict``

        :returns: ``bool``

        :raises: :class:`.PlumberyException`

        """

        if 'domain' not in blueprint or type(blueprint['domain']) is not dict:
            raise PlumberyException(
                "Error: no network domain has been defined " \
                     "for the blueprint '{}'!".format(blueprint['target']))

        domainName = blueprint['domain']['name']
        domain = None
        for domain in self.region.ex_list_network_domains(
                                        location=self.facility.location):
            if domain.name == domainName:
                break

        if domain is None or domain.name != domainName:
            return False

        if 'ethernet' not in blueprint or type(blueprint['ethernet']) is not dict:
            raise PlumberyException(
                "Error: no ethernet network has been defined " \
                        "for the blueprint '{}'!".format(blueprint['target']))

        networkName = blueprint['ethernet']['name']
        network = None
        for network in self.region.ex_list_vlans(
                                    location=self.facility.location,
                                    network_domain=domain):
            if network.name == networkName:
                break

        if network is not None and network.name == networkName:

            if self.plumbery.safeMode:
                logging.info("Would have destroyed Ethernet network '{}' "
                                "if not in safe mode".format(networkName))
                return False

            logging.info("Destroying Ethernet network '{}'".format(networkName))

            while True:
                try:
                    self.region.ex_delete_vlan(vlan=network)
                    logging.info("- in progress")

                except Exception as feedback:

                    if 'RESOURCE_BUSY' in str(feedback):
                        time.sleep(10)
                        continue

                    elif 'RESOURCE_NOT_FOUND' in str(feedback):
                        logging.info("- not found")

                    elif 'HAS_DEPENDENCY' in str(feedback):
                        logging.info("- not now")
                        return False

                    else:
                        raise PlumberyException("Error: unable to destroy " \
                                    "Ethernet network '{0}' {1}!"
                                            .format(networkName, feedback))

                break

        if self.plumbery.safeMode:
            logging.info("Would have destroyed network domain '{}' "
                            "if not in safe mode".format(domainName))
            return False

        logging.info("Destroying network domain '{}'".format(domainName))

        while True:
            try:
                self.region.ex_delete_network_domain(network_domain=domain)
                logging.info("- in progress")

            except Exception as feedback:

                if 'RESOURCE_BUSY' in str(feedback):
                    time.sleep(10)
                    continue

                elif 'RESOURCE_NOT_FOUND' in str(feedback):
                    logging.info("- not found")

                elif 'HAS_DEPENDENCY' in str(feedback):
                    logging.info("- not now")
                    return False

                raise PlumberyException(
                    "Error: unable to destroy network domain '{0}' {1}!"
                                    .format(domainName, feedback))

            break

        return True

    def get_domain(self, blueprint):
        """
        Retrieves a domain attached to a blueprint

        :param blueprint: the various attributes of the target fittings
        :type blueprint: ``dict``

        :returns: :class:`.PlumberyDomain` or None

        :raises: :class:`.PlumberyException`

        """
        target = PlumberyDomain(self.facility)

        if 'domain' not in blueprint or type(blueprint['domain']) is not dict:
            raise PlumberyException(
                "Error: no network domain has been defined " \
                     "for the blueprint '{}'!".format(blueprint['target']))

        domainName = blueprint['domain']['name']
        target.domain = None
        for target.domain in self.region.ex_list_network_domains(
                                        location=self.facility.location):
            print target.domain.name
            if target.domain.name == domainName:
                break

        if target.domain is None or target.domain.name != domainName:
            return None

        if 'ethernet' not in blueprint or type(blueprint['ethernet']) is not dict:
            raise PlumberyException(
                "Error: no ethernet network has been defined " \
                        "for the blueprint '{}'!".format(blueprint['target']))

        if 'subnet' not in blueprint['ethernet']:
            raise PlumberyException("Error: no IPv4 subnet " \
                "(e.g., '10.0.34.0') as been defined for the blueprint '{}'!"
                                                .format(blueprint['target']))

        networkName = blueprint['ethernet']['name']
        target.network = None
        for target.network in self.region.ex_list_vlans(
                                            location=self.facility.location,
                                            network_domain=target.domain):
            if target.network.name == networkName:
                break

        if target.network is None or target.network.name != networkName:
            return None

        return target

