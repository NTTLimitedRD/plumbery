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
from uuid import uuid4

try:
    from lxml import etree as ET
except ImportError:
    from xml.etree import ElementTree as ET

from libcloud.common.dimensiondata import DimensionDataFirewallRule
from libcloud.common.dimensiondata import DimensionDataFirewallAddress
from libcloud.common.dimensiondata import DimensionDataNatRule
from libcloud.common.dimensiondata import TYPES_URN
from libcloud.loadbalancer.base import Algorithm
from libcloud.loadbalancer.base import Member
from libcloud.loadbalancer.types import Provider
from libcloud.loadbalancer.types import State
from libcloud.loadbalancer.providers import get_driver as get_balancer_factory

from libcloud.utils.xml import fixxpath, findtext, findall

from exceptions import PlumberyException

__all__ = ['PlumberyDomain']


class PlumberyDomain:
    """
    Cloud automation for a network domain

    :param facility: the underlying physical facility
    :type facility: :class:`plumbery.PlumberyFacility`

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

        self._cache_remote_vlan = []
        self._cache_offshore_vlan = []
        self._cache_firewall_rules = []

        self._network_domains_already_built = []
        self._vlans_already_built = []

    def _add_to_balancer(self, node):
        """
        Adds a node to a load balancer

        """

        if 'balancer' not in self.blueprint:
            return True

        if 'port' in self.blueprint['balancer']:
            port = self.blueprint['balancer']['port']
        else:
            port = '80'

        ports = str(port).split(' ')
        for port in ports:
            port = int(port)
            if port < 1 or port > 65535:
                raise PlumberyException(
                    "Error: invalid balancer port has been defined "
                    "for the blueprint '{}'!".format(self.blueprint['target']))

        factory = get_balancer_factory(Provider.DIMENSIONDATA)
        driver = factory(
            self.plumbery.get_user_name(),
            self.plumbery.get_user_password(),
            region=self.facility.fittings.regionId)

        domain = self.get_network_domain(self.blueprint['domain']['name'])
        driver.ex_set_current_network_domain(domain.id)

        for port in ports:

            name = self._name_load_balancer(port)

            if self.plumbery.safeMode:
                logging.info("Would have added '{}' to load balancer '{}' "
                             "if not in safe mode".format(node.name, name))
                continue

            try:
                logging.info("Adding '{}' to load balancer '{}'"
                             .format(node.name, name))
#                driver.create_balancer(name=name,
#                                      algorithm=algorithms[algorithm],
#                                      port=int(port),
#                                      protocol=protocol,
#                                      members=None)
                logging.info("- in progress")

            except Exception as feedback:

                if 'NAME_NOT_UNIQUE' in str(feedback):
                    logging.info("- already done")

                elif 'NO_IP_ADDRESS_AVAILABLE' in str(feedback):
                    logging.info("- no more ipv4 address available -- assign more")

                else:
                    logging.info("- unable to create load balancer")
                    logging.info(str(feedback))

        return True

    def _attach_node(self, node, networks):
        """
        Glues a node to multiple networks

        :param node: the target node
        :type node: :class:`libcloud.compute.base.Node`

        :param networks: a list of networks to connect, and ``internet``
        :type networks: list of ``str``

        This function adds network interfaces to a node, or adds address
        translation to the public Internet.

        Example in the fittings plan::

          - web:
              domain:
                ipv4: 6
              ethernet:
                name: gigafox.data
              nodes:
                - web[10..12]:
                    glue:
                      - gigafox.control
                      - internet 80 443

        In this example, another network interface is added to each node for
        connection to the Ethernet network ``gigafox.control``.

        Also, public IPv4 addresses are mapped on private addresses, so that
        each node web10, web11 and web12 is reachable from the internet.
        Public IPv4 addresses are taken from pool declared at the domain level,
        with the attribute ``ipv4``. In the example above, 6 addresses are
        assigned to the network domain, of which 3 are given to web nodes.

        If one or multiple numbers are mentioned after the network name, they
        are used to configure the firewall appropriately.

        """

        hasChanged = False

        if node is None:
            return hasChanged

        for line in networks:

            tokens = line.split(' ')
            label = tokens.pop(0)

            if self.plumbery.safeMode:
                logging.info("Would have glued node '{}' to network '{}' "
                             "if not in safe mode".format(node.name, label))
                continue

            if label == 'internet':
                self._attach_node_to_internet(node, tokens)
                continue

            logging.info("Glueing node '{}' to network '{}'"
                         .format(node.name, label))
            target = self.get_ethernet(label.split('::'))
            if not target:
                logging.info("- network '{}' is unknown".format(label))
                continue

            while True:
                try:
                    self.region.ex_attach_node_to_vlan(node, target)
                    logging.info("- in progress")
                    hasChanged = True

                except Exception as feedback:

                    if 'RESOURCE_BUSY' in str(feedback):
                        time.sleep(10)
                        continue

                    elif 'RESOURCE_LOCKED' in str(feedback):
                        logging.info("- not now - locked")

                    elif 'INVALID_INPUT_DATA' in str(feedback):
                        logging.info("- already done")

                    else:
                        logging.info("- unable to glue node")
                        logging.info(str(feedback))

                break

        return hasChanged

    def _attach_node_to_internet(self, node, ports=[]):
        """
        Adds address translation for one node

        :param node: node that has to be reachable from the internet
        :type node: :class:`libcloud.common.Node`

        :param ports: the ports that have to be opened
        :type ports: a list of ``str``

        """

        domain = self.get_network_domain(self.blueprint['domain']['name'])

        internal_ip = node.private_ips[0]

        external_ip = None
        for rule in self.region.ex_list_nat_rules(domain):
            if rule.internal_ip == internal_ip:
                external_ip = rule.external_ip
                logging.info("Making node '{}' reachable from the internet"
                             .format(node.name))
                logging.info("- node is reachable at '{}'".format(external_ip))

        if external_ip is None:
            external_ip = self._get_ipv4()

            if external_ip is None:
                logging.info("Making node '{}' reachable from the internet"
                             .format(node.name))
                logging.info("- no more ipv4 address available -- assign more")
                return

            logging.info("Making node '{}' reachable from the internet"
                         .format(node.name))
            while True:
                try:
                    self.region.ex_create_nat_rule(
                                            domain,
                                            internal_ip,
                                            external_ip)
                    logging.info("- node is reachable at '{}'".format(external_ip))

                except Exception as feedback:
                    if 'RESOURCE_BUSY' in str(feedback):
                        time.sleep(10)
                        continue

                    elif 'RESOURCE_LOCKED' in str(feedback):
                        logging.info("- not now - locked")
                        return

                    else:
                        logging.info("- unable to add address translation")
                        logging.info(str(feedback))

                break

        candidates = self._list_candidate_firewall_rules(node, ports)

        for rule in self._list_firewall_rules():

            if rule.name in candidates.keys():
                logging.info("Creating firewall rule '{}'"
                             .format(rule.name))
                logging.info("- already done")
                candidates = {k:candidates[k] for k in candidates if k != rule.name}

        for name, rule in candidates.items():

            if self.plumbery.safeMode:
                logging.info("Would have created firewall rule '{}' "
                             "if not in safe mode".format(name))

            else:
                logging.info("Creating firewall rule '{}'"
                             .format(name))

                try:

                    self._ex_create_firewall_rule(
                                network_domain=domain,
                                rule=rule,
                                position='LAST')

                    logging.info("- in progress")

                except Exception as feedback:

                    if 'NAME_NOT_UNIQUE' in str(feedback):
                        logging.info("- already done")

                    else:
                        logging.info("- unable to create firewall rule")
                        logging.info(str(feedback))

    def build(self, blueprint):
        """
        Creates a network domain if needed.

        :param blueprint: the various attributes of the target fittings
        :type blueprint: ``dict``

        :returns: ``bool``
            - True if the network has been created or is already there,
            False otherwise

        :raises: :class:`plumbery.PlumberyException`
            - if some unrecoverable error occurs

        This function is looking at all fittings in the blueprint except the
        nodes. This is including:

        * the network domain itself
        * one or multiple Ethernet networks

        In safe mode, the function will stop on any missing component since
        it is not in a position to add fittings, and return ``False``.
        If all components already exist then the funciton will return ``True``.

        """

        self.blueprint = blueprint

        if 'domain' not in blueprint or type(blueprint['domain']) is not dict:
            raise PlumberyException(
                "Error: no network domain has been defined "
                "for the blueprint '{}'!".format(blueprint['target']))

        domainName = blueprint['domain']['name']

        if 'ethernet' not in blueprint                                      \
           or type(blueprint['ethernet']) is not dict:
            raise PlumberyException(
                        "Error: no ethernet network has been defined "
                        "for the blueprint '{}'!".format(blueprint['target']))

        if 'subnet' not in blueprint['ethernet']:
            raise PlumberyException(
                "Error: no IPv4 subnet "
                "(e.g., '10.0.34.0') as been defined for the blueprint '{}'!"
                .format(blueprint['target']))

        networkName = blueprint['ethernet']['name']

        self.domain = self.get_network_domain(domainName)
        if self.domain is not None:
            logging.info("Creating network domain '{}'".format(domainName))
            logging.info("- already done")

        elif self.plumbery.safeMode:
            logging.info("Would have created network domain '{}' "
                         "if not in safe mode".format(domainName))
            logging.info("Would have created Ethernet network '{}' "
                         "if not in safe mode".format(networkName))
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

                    # prevent locks in xops
                    self.region.ex_wait_for_state(
                                'NORMAL', self.region.ex_get_network_domain,
                                poll_interval=5, timeout=1200,
                                network_domain_id=self.domain.id)

                    self.facility._cache_network_domains.append(self.domain)

                except Exception as feedback:

                    if 'RESOURCE_BUSY' in str(feedback):
                        time.sleep(10)
                        continue

                    elif 'OPERATION_NOT_SUPPORTED' in str(feedback):
                        logging.info("- operation not supported")
                        return False

                    elif 'RESOURCE_LOCKED' in str(feedback):
                        logging.info("- not now - locked")
                        return False

                    else:
                        logging.info("- unable to create network domain")
                        logging.info(str(feedback))
                        return False

                break

        self.network = self.get_ethernet(networkName)
        if self.network is not None:
            logging.info("Creating Ethernet network '{}'"
                         .format(networkName))
            logging.info("- already done")

        elif self.plumbery.safeMode:
            logging.info("Would have created Ethernet network '{}' "
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

                    # prevent locks in xops
                    self.region.ex_wait_for_state('NORMAL',
                                                self.region.ex_get_vlan,
                                                poll_interval=5, timeout=1200,
                                                vlan_id=self.network.id)

                    self._update_ipv6(self.network)
                    self.facility._cache_vlans.append(self.network)

                except Exception as feedback:

                    if 'RESOURCE_BUSY' in str(feedback):
                        time.sleep(10)
                        continue

                    elif 'NAME_NOT_UNIQUE' in str(feedback):
                        logging.info("- not possible "
                                     "- network already exists elsewhere")

                    elif 'IP_ADDRESS_NOT_UNIQUE' in str(feedback):
                        logging.info("- not possible "
                                     "- subnet is used elsewhere")

                    elif 'RESOURCE_LOCKED' in str(feedback):
                        logging.info("- not now - locked")
                        return False

                    else:
                        logging.info("- unable to create Ethernet network")
                        logging.info(str(feedback))
                        return False

                break

        return True

    def _build_firewall_rules(self):
        """
        Changes firewall settings to accept incoming traffic

        This function adds firewall rules to allow traffic towards given
        network. It looks at the ``accept`` settings in the blueprint to
        identify all source networks.

        Example in the fittings plan::

          - web:
              domain: *vdc1
              ethernet:
                name: gigafox.production
                accept:
                  - gigafox.control
                  - dd-eu::EU6::other.network.there

        In this example, the firewall is configured so that any ip traffic
        from the Ethernet network ``gigafox.control`` can reach the Ethernet
        network ``gigafox.production``. One rule is created for
        IPv4 and another rule is created for IPv6.

        The second network that is configured is from another data centre
        in another region. This is leveraging the private network that
        interconnect all MCPs. For networks outside the current domain, only
        one rule is added to allow IPv6 traffic. This is because IPv4 routing
        is not allowed across multiple network domains.

        """

        if 'accept' not in self.blueprint['ethernet']:
            return True

        destination = self.get_ethernet(self.blueprint['ethernet']['name'])
        if not destination:
            return True

        destinationIPv4 = DimensionDataFirewallAddress(
                    any_ip=False,
                    ip_address=destination.private_ipv4_range_address,
                    ip_prefix_size=destination.private_ipv4_range_size,
                    port_begin=None,
                    port_end=None)

        destinationIPv6 = DimensionDataFirewallAddress(
                    any_ip=False,
                    ip_address=destination.ipv6_range_address,
                    ip_prefix_size=destination.ipv6_range_size,
                    port_begin=None,
                    port_end=None)

        for item in self.blueprint['ethernet']['accept']:

            if isinstance(item, dict):
                label = item.keys()[0]
            else:
                label = str(item)

            source = self.get_ethernet(label.split('::'))
            if not source:
                logging.info("Source network '{}' is unknown".format(label))
                continue

            ruleIPv4Name = self.name_firewall_rule(
                                        source.name, destination.name, 'IP')

            shouldCreateRuleIPv4 = True
            if source.location.name != destination.location.name:
                shouldCreateRuleIPv4 = False
            elif source.network_domain.name != destination.network_domain.name:
                shouldCreateRuleIPv4 = False

            ruleIPv6Name = self.name_firewall_rule(
                                        source.name, destination.name, 'IPv6')

            shouldCreateRuleIPv6 = True

            for rule in self._list_firewall_rules():

                if shouldCreateRuleIPv4 and rule.name.lower() == ruleIPv4Name.lower():
                    logging.info("Creating firewall rule '{}'"
                                 .format(rule.name))
                    logging.info("- already done")
                    shouldCreateRuleIPv4 = False
                    continue

                if shouldCreateRuleIPv6 and rule.name.lower() == ruleIPv6Name.lower():
                    logging.info("Creating firewall rule '{}'"
                                 .format(rule.name))
                    logging.info("- already done")
                    shouldCreateRuleIPv6 = False
                    continue

            if shouldCreateRuleIPv4:

                if self.plumbery.safeMode:
                    logging.info("Would have created firewall rule '{}' "
                                 "if not in safe mode".format(ruleIPv4Name))

                else:
                    logging.info("Creating firewall rule '{}'"
                                 .format(ruleIPv4Name))

                    sourceIPv4 = DimensionDataFirewallAddress(
                                any_ip=False,
                                ip_address=source.private_ipv4_range_address,
                                ip_prefix_size=source.private_ipv4_range_size,
                                port_begin=None,
                                port_end=None)

                    ruleIPv4 = DimensionDataFirewallRule(
                                    id=uuid4(),
                                    action='ACCEPT_DECISIVELY',
                                    name=ruleIPv4Name,
                                    location=destination.location,
                                    network_domain=destination.network_domain,
                                    status='NORMAL',
                                    ip_version='IPV4',
                                    protocol='IP',
                                    enabled='true',
                                    source=sourceIPv4,
                                    destination=destinationIPv4)

                    try:

                        self._ex_create_firewall_rule(
                                    network_domain=destination.network_domain,
                                    rule=ruleIPv4,
                                    position='LAST')

                        logging.info("- in progress")

                    except Exception as feedback:

                        if 'NAME_NOT_UNIQUE' in str(feedback):
                            logging.info("- already done")

                        else:
                            logging.info("- unable to create firewall rule")
                            logging.info(str(feedback))

            if shouldCreateRuleIPv6:

                if self.plumbery.safeMode:
                    logging.info("Would have created firewall rule '{}' "
                                 "if not in safe mode".format(ruleIPv4Name))

                else:
                    logging.info("Creating firewall rule '{}'"
                                 .format(ruleIPv6Name))

                    sourceIPv6 = DimensionDataFirewallAddress(
                                    any_ip=False,
                                    ip_address=source.ipv6_range_address,
                                    ip_prefix_size=source.ipv6_range_size,
                                    port_begin=None,
                                    port_end=None)

                    ruleIPv6 = DimensionDataFirewallRule(
                                    id=uuid4(),
                                    action='ACCEPT_DECISIVELY',
                                    name=ruleIPv6Name,
                                    location=destination.location,
                                    network_domain=destination.network_domain,
                                    status='NORMAL',
                                    ip_version='IPV6',
                                    protocol='IP',
                                    enabled='true',
                                    source=sourceIPv6,
                                    destination=destinationIPv6)

                    try:

                        self._ex_create_firewall_rule(
                                    network_domain=destination.network_domain,
                                    rule=ruleIPv6,
                                    position='LAST')

                        logging.info("- in progress")

                    except Exception as feedback:

                        if 'NAME_NOT_UNIQUE' in str(feedback):
                            logging.info("- already done")

                        else:
                            logging.info("- unable to create firewall rule")
                            logging.info(str(feedback))

        return True

    def _build_balancer(self):
        """
        Adds a load balancer for nodes in the blueprint

        Example in the fittings plan::

          - web:
              domain: *vdc1
              ethernet: *data
              nodes:
                - apache[10..19]
              balancer:
                port: 80 443
                protocol: http
                members: apache[10..19]
                algorithm: round_robin

        In this example, the load balancer is configured to accept web traffic
        and to distribute the workload across multiple web engines.

        The algorithm can take any value among followings:

        * random
        * round_robin
        * least_connections
        * weighted_round_robin
        * weighted_least_connections
        * shortest_response
        * persistent_ip

        """

        if 'balancer' not in self.blueprint:
            return True

        if 'port' in self.blueprint['balancer']:
            port = self.blueprint['balancer']['port']
        else:
            port = '80'

        ports = str(port).split(' ')
        for port in ports:
            port = int(port)
            if port < 1 or port > 65535:
                raise PlumberyException(
                    "Error: invalid balancer port has been defined "
                    "for the blueprint '{}'!".format(self.blueprint['target']))

        if 'protocol' in self.blueprint['balancer']:
            protocol = self.blueprint['balancer']['protocol']
        else:
            protocol = 'http'

        protocols = ['http', 'https', 'tcp', 'udp']

        if protocol not in protocols:
            raise PlumberyException(
                "Error: unknown balancer protocol has been defined "
                "for the blueprint '{}'!".format(self.blueprint['target']))

        if 'algorithm' in self.blueprint['balancer']:
            algorithm = self.blueprint['balancer']['algorithm']
        else:
            algorithm = 'round_robin'

        algorithms = {
            'random': Algorithm.RANDOM,
            'round_robin': Algorithm.ROUND_ROBIN,
            'least_connections': Algorithm.LEAST_CONNECTIONS,
            'weighted_round_robin': Algorithm.WEIGHTED_ROUND_ROBIN,
            'weighted_least_connections': Algorithm.WEIGHTED_LEAST_CONNECTIONS,
            'shortest_response': Algorithm.SHORTEST_RESPONSE,
            'persistent_ip': Algorithm.PERSISTENT_IP}

        if algorithm not in algorithms.keys():
            raise PlumberyException(
                "Error: unknown balancer algorithm has been defined "
                "for the blueprint '{}'!".format(self.blueprint['target']))

        factory = get_balancer_factory(Provider.DIMENSIONDATA)
        driver = factory(
            self.plumbery.get_user_name(),
            self.plumbery.get_user_password(),
            region=self.facility.fittings.regionId)

        domain = self.get_network_domain(self.blueprint['domain']['name'])
        driver.ex_set_current_network_domain(domain.id)

        for port in ports:

            name = self._name_load_balancer(port)

            if self.plumbery.safeMode:
                logging.info("Would have created load balancer '{}' "
                             "if not in safe mode".format(name))
                continue

            try:
                logging.info("Creating load balancer '{}'".format(name))
                driver.create_balancer(name=name,
                                      algorithm=algorithms[algorithm],
                                      port=int(port),
                                      protocol=protocol,
                                      members=None)
                logging.info("- in progress")

            except Exception as feedback:

                if 'NAME_NOT_UNIQUE' in str(feedback):
                    logging.info("- already done")

                elif 'NO_IP_ADDRESS_AVAILABLE' in str(feedback):
                    logging.info("- no more ipv4 address available -- assign more")

                else:
                    logging.info("- unable to create load balancer")
                    logging.info(str(feedback))

        return True

    def _destroy_firewall_rules(self):
        """
        Destroys firewall rules

        """

        if 'accept' not in self.blueprint['ethernet']:
            return True

        destinationLabel = self.blueprint['ethernet']['name']

        for item in self.blueprint['ethernet']['accept']:

            if isinstance(item, dict):
                label = item.keys()[0]
            else:
                label = str(item)

            sourceLabel = label

            ruleIPv4Name = self.name_firewall_rule(
                                        sourceLabel, destinationLabel, 'IP')

            ruleIPv6Name = self.name_firewall_rule(
                                        sourceLabel, destinationLabel, 'IPv6')

            for rule in self._list_firewall_rules():

                if rule.name == ruleIPv4Name or rule.name == ruleIPv6Name:

                    if self.plumbery.safeMode:
                        logging.info("Would have destroyed firewall rule '{}' "
                                     "if not in safe mode".format(rule.name))

                    else:
                        logging.info("Destroying firewall rule '{}'"
                                     .format(rule.name))
                        self.region.ex_delete_firewall_rule(rule)
                        logging.info("- in progress")

    def _destroy_balancer(self):
        """
        Destroys load balancer

        """

        if 'balancer' not in self.blueprint['ethernet']:
            return True

        if 'balancer' not in self.blueprint:
            return True

        if 'port' in self.blueprint['balancer']:
            port = self.blueprint['balancer']['port']
        else:
            port = '80'

        ports = port.split(' ')
        for port in ports:
            port = int(port)
            if port < 1 or port > 65535:
                raise PlumberyException(
                    "Error: invalid balancer port has been defined "
                    "for the blueprint '{}'!".format(self.blueprint['target']))

        factory = get_balancer_factory(Provider.DIMENSIONDATA)
        driver = factory(
            self.plumbery.get_user_name(),
            self.plumbery.get_user_password(),
            region=self.facility.fittings.regionId)

        domain = self.get_network_domain(self.blueprint['domain']['name'])
        driver.ex_set_current_network_domain(domain.id)

        candidates = []
        for port in ports:
            candidates.append(self._name_load_balancer(port))
        logging.info(candidates)

        logger.info("balancers")
        balancers = driver.list_balancers()
        print(balancers)
        for balancer in balancers:
            logger.info("balancer")
            logger.info(balancer)
            continue

            if self.plumbery.safeMode:
                logging.info("Would have destroyed load balancer '{}' "
                             "if not in safe mode".format(balancer.name))
                continue

            try:
                logging.info("Destroying load balancer '{}'".format(balancer.name))
                driver.destroy_balancer(balancer)
                logging.info("- in progress")

            except Exception as feedback:

                if 'NAME_NOT_UNIQUE' in str(feedback):
                    logging.info("- already done")

                else:
                    logging.info("- unable to create load balancer")
                    logging.info(str(feedback))

    def destroy_blueprint(self, blueprint):
        """
        Destroys network and security elements of a blueprint

        :param blueprint: the various attributes of the target fittings
        :type blueprint: ``dict``

        :returns: ``bool``

        This function looks after following service elements:

        * it releases public IPv4 addresses
        * it destroys firewall rules
        * it destroys the Ethernet network
        * it destroys the network domain

        The destruction is tentative, meaning that if the Ethernet network or
        the network domain have some dependency then they cannot be destroyed.
        This is happenign quite often since multiple blueprints can share the
        same Ethernet network or the same network domain.

        """

        self.blueprint = blueprint

        if 'domain' not in blueprint or type(blueprint['domain']) is not dict:
            raise PlumberyException(
                "Error: no network domain has been defined "
                "for the blueprint '{}'!".format(blueprint['target']))

        if 'ethernet' not in blueprint or type(blueprint['ethernet']) is not dict:
            raise PlumberyException(
                "Error: no ethernet network has been defined "
                "for the blueprint '{}'!".format(blueprint['target']))

        domainName = blueprint['domain']['name']
        networkName = blueprint['ethernet']['name']

        domain = self.get_network_domain(domainName)
        if domain is None:
            logging.info("Destroying Ethernet network '{}'".format(networkName))
            logging.info("- not found")
            logging.info("Destroying network domain '{}'".format(domainName))
            logging.info("- not found")
            return False

        self._destroy_firewall_rules()

        self._destroy_balancer()

        self._release_ipv4()

        network = self.get_ethernet(networkName)
        if network is None:
            logging.info("Destroying Ethernet network '{}'".format(networkName))
            logging.info("- not found")

        elif self.plumbery.safeMode:
            logging.info("Would have destroyed Ethernet network '{}' "
                         "if not in safe mode".format(networkName))

        else:
            logging.info("Destroying Ethernet network '{}'".format(networkName))

            retry = True
            while True:
                try:
                    self.region.ex_delete_vlan(vlan=network)
                    logging.info("- in progress")

                    while True:
                        try:
                            time.sleep(10)
                            self.region.ex_get_vlan(vlan_id=network.id)
                        except Exception as feedback:
                            if 'RESOURCE_NOT_FOUND' in str(feedback):
                                break

                except Exception as feedback:

                    if 'RESOURCE_BUSY' in str(feedback):
                        time.sleep(10)
                        continue

                    elif 'RESOURCE_NOT_FOUND' in str(feedback):
                        logging.info("- not found")

                    elif 'HAS_DEPENDENCY' in str(feedback):

                        # give time to ensure nodes have been deleted
                        if retry:
                            retry = False
                            time.sleep(30)
                            continue

                        logging.info("- not now - stuff on it")
                        return False

                    elif 'RESOURCE_LOCKED' in str(feedback):
                        logging.info("- not now - locked")
                        logging.info(feedback)
                        return False

                    else:
                        logging.info("- unable to destroy Ethernet network")
                        logging.info(str(feedback))
                        return False

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
                    logging.info("- not now - stuff on it")
                    return False

                elif 'RESOURCE_LOCKED' in str(feedback):
                    logging.info("- not now - locked")
                    return False

                else:
                    logging.info("- unable to destroy Ethernet network")
                    logging.info(str(feedback))
                    return False

            break

        return True

    def _detach_node_from_internet(self, node):
        """
        Destroys address translation for one node

        :param node: node that was reachable from the internet
        :type node: :class:`libcloud.common.Node`

        """

        internal_ip = node.private_ips[0]
        domain = self.get_network_domain(self.blueprint['domain']['name'])
        for rule in self.region.ex_list_nat_rules(domain):
            if rule.internal_ip == internal_ip:

                while True:
                    try:
                        logging.info("Detaching node '{}' from the internet"
                                     .format(node.name))
                        self.region.ex_delete_nat_rule(rule)
                        logging.info("- in progress")

                    except Exception as feedback:
                        if 'RESOURCE_BUSY' in str(feedback):
                            time.sleep(10)
                            continue

                        elif 'RESOURCE_LOCKED' in str(feedback):
                            logging.info("- not now - locked")
                            return

                        else:
                            logging.info("- unable to remove address translation")
                            logging.info(str(feedback))

                    break

        for rule in self._list_firewall_rules():

            if '_'+node.name.lower() in rule.name.lower():

                if self.plumbery.safeMode:
                    logging.info("Would have destroyed firewall rule '{}' "
                                 "if not in safe mode".format(rule.name))

                else:
                    logging.info("Destroying firewall rule '{}'"
                                 .format(rule.name))
                    self.region.ex_delete_firewall_rule(rule)
                    logging.info("- in progress")

    def _ex_create_firewall_rule(self, network_domain, rule, position):
        create_node = ET.Element('createFirewallRule', {'xmlns': TYPES_URN})
        ET.SubElement(create_node, "networkDomainId").text = network_domain.id
        ET.SubElement(create_node, "name").text = rule.name
        ET.SubElement(create_node, "action").text = rule.action
        ET.SubElement(create_node, "ipVersion").text = rule.ip_version
        ET.SubElement(create_node, "protocol").text = rule.protocol
        # Setup source port rule
        source = ET.SubElement(create_node, "source")
        source_ip = ET.SubElement(source, 'ip')
        if rule.source.any_ip:
            source_ip.set('address', 'ANY')
        else:
            source_ip.set('address', rule.source.ip_address)
            source_ip.set('prefixSize', str(rule.source.ip_prefix_size))
            if rule.source.port_begin is not None:
                source_port = ET.SubElement(source, 'port')
                source_port.set('begin', rule.source.port_begin)
            if rule.source.port_end is not None:
                source_port.set('end', rule.source.port_end)
        # Setup destination port rule
        dest = ET.SubElement(create_node, "destination")
        dest_ip = ET.SubElement(dest, 'ip')
        if rule.destination.any_ip:
            dest_ip.set('address', 'ANY')
        else:
            dest_ip.set('address', rule.destination.ip_address)
            if rule.destination.ip_prefix_size is not None:
                dest_ip.set('prefixSize', str(rule.destination.ip_prefix_size))
            if rule.destination.port_begin is not None:
                dest_port = ET.SubElement(dest, 'port')
                dest_port.set('begin', rule.destination.port_begin)
            if rule.destination.port_end is not None:
                dest_port.set('end', rule.destination.port_end)
        ET.SubElement(create_node, "enabled").text = 'true'
        placement = ET.SubElement(create_node, "placement")
        placement.set('position', position)

        response = self.region.connection.request_with_orgId_api_2(
            'network/createFirewallRule',
            method='POST',
            data=ET.tostring(create_node)).object

        rule_id = None
        for info in findall(response, 'info', TYPES_URN):
            if info.get('name') == 'firewallRuleId':
                rule_id = info.get('value')
        rule.id = rule_id
        return rule

    def get_container(self, blueprint):
        """
        Retrieves a domain attached to a blueprint

        :param blueprint: the various attributes of the target fittings
        :type blueprint: ``dict``

        :returns: :class:`plumbery.PlumberyDomain` or `None``

        The returned object has at least a network domain and an Ethernet
        network, like in the following example::

            container = domains.get_container(blueprint)
            print container.domain.name
            print container.network.name

        """
        target = PlumberyDomain(self.facility)

        target.blueprint = blueprint

        if 'domain' not in blueprint or type(blueprint['domain']) is not dict:
            raise PlumberyException(
                "Error: no network domain has been defined "
                "for the blueprint '{}'!".format(blueprint['target']))

        if 'ethernet' not in blueprint or type(blueprint['ethernet']) is not dict:
            raise PlumberyException(
                "Error: no ethernet network has been defined "
                "for the blueprint '{}'!".format(blueprint['target']))

        domainName = blueprint['domain']['name']
        target.domain = self.get_network_domain(domainName)

        networkName = blueprint['ethernet']['name']
        target.network = self.get_ethernet(networkName)

        return target

    def get_ethernet(self, path):
        """
        Retrieves an Ethernet network by name

        :param label: the name of the target Ethernet network
        :type label: ``str`` or ``list``of ``str``

        :returns: :class:`VLAN` or None

        This function searches firstly at the current facility. If the
        name is a complete path to a remote network, then plumbery looks
        there. If a different region is provided, then authentication is done
        against the related endpoint.

        For example if ``MyNetwork`` has been defined in a data centre in
        Europe::

            >>>domains.get_ethernet('MyNetwork')
            >>>domains.get_ethernet(['EU6', 'MyNetwork'])
            Looking for remote Ethernet network 'EU6::MyNetwork'
            - found it
            >>>domains.get_ethernet(['dd-eu', 'EU6', 'MyNetwork'])
            Looking for offshore Ethernet network 'dd-eu::EU6::MyNetwork'
            - found it

        """

        if isinstance(path, str):
            path = [path]

        if len(path) == 1:

            if len(self.facility._cache_vlans) < 1:
                logging.info("Listing Ethernet networks")
                self.facility._cache_vlans = self.region.ex_list_vlans(
                                            location=self.facility.location)
                for network in self.facility._cache_vlans:
                    self._update_ipv6(network)
                logging.info("- found {} Ethernet networks"
                             .format(len(self.facility._cache_vlans)))

            for network in self.facility._cache_vlans:
                if network.name == path[0]:
                    return network

        elif len(path) == 2:

            if len(self._cache_remote_vlan) == 3                            \
                            and self._cache_remote_vlan[0] == path[0]       \
                            and self._cache_remote_vlan[1] == path[1]:
                return self._cache_remote_vlan[2]

            logging.info("Looking for remote Ethernet network '{}'"
                         .format('::'.join(path)))

            remoteLocation = self.region.ex_get_location_by_id(path[0])

            vlans = self.region.ex_list_vlans(location=remoteLocation)
            for network in vlans:
                if network.name == path[1]:
                    self._update_ipv6(network)
                    self._cache_remote_vlan += path
                    self._cache_remote_vlan.append(network)
                    logging.info("- found it")
                    return network

        elif len(path) == 3:

            if len(self._cache_offshore_vlan) == 4                            \
                            and self._cache_offshore_vlan[0] == path[0]       \
                            and self._cache_offshore_vlan[1] == path[1]       \
                            and self._cache_offshore_vlan[2] == path[2]:
                return self._cache_offshore_vlan[3]

            logging.info("Looking for offshore Ethernet network '{}'"
                         .format('::'.join(path)))

            offshore = self.plumbery.provider(
                self.plumbery.get_user_name(),
                self.plumbery.get_user_password(),
                region=path[0])

            remoteLocation = offshore.ex_get_location_by_id(path[1])

            vlans = offshore.ex_list_vlans(location=remoteLocation)
            for network in vlans:
                if network.name == path[2]:
                    self._update_ipv6(network, offshore)
                    self._cache_offshore_vlan += path
                    self._cache_offshore_vlan.append(network)
                    logging.info("- found it")
                    return network

        return None

    def _get_ipv4(self):
        """
        Provides a free public IPv4 if possible

        """

        addresses = self._list_ipv4()
        if len(addresses) < 1:
            self._reserve_ipv4()
            addresses = self._list_ipv4()

        domain = self.get_network_domain(self.blueprint['domain']['name'])

        for rule in self.region.ex_list_nat_rules(domain):
            addresses.remove(rule.external_ip)

        if len(addresses) < 1:
            return None

        return addresses[0]

    def get_network_domain(self, name):
        """
        Retrieves a network domain by name

        :param name: name of the target network domain
        :type name: ``str``

        """

        if len(self.facility._cache_network_domains) < 1:
            logging.info("Listing network domains")
            self.facility._cache_network_domains = self.region.ex_list_network_domains(
                                                        self.facility.location)
            logging.info("- found {} network domains"
                         .format(len(self.facility._cache_network_domains)))

        for domain in self.facility._cache_network_domains:
            if domain.name == name:
                return domain

        return None

    def _list_candidate_firewall_rules(self, node, ports=[]):
        """
        Lists rules that should apply to one node

        :param node: node that has to be reachable from the internet
        :type node: :class:`libcloud.common.Node`

        :param ports: the ports that have to be opened
        :type ports: a list of ``str``

        """

        domain = self.get_network_domain(self.blueprint['domain']['name'])
        network = self.get_ethernet(self.blueprint['ethernet']['name'])

        internal_ip = node.private_ips[0]

        external_ip = None
        for rule in self.region.ex_list_nat_rules(domain):
            if rule.internal_ip == internal_ip:
                external_ip = rule.external_ip

        if external_ip is None:
            return {}

        candidates = {}

        if len(ports) < 1:
            ports = ['any']

        for port in ports:

            tokens = port.split('..')
            if len(tokens) == 1:
                if tokens[0].lower() == 'any':
                    port_begin = None
                else:
                    port_begin = tokens[0]
                port_end = None
                port = tokens[0]
            else:
                port_begin = tokens[0]
                port_end = tokens[1]
                port = port_begin+'..'+port_end

            ruleIPv4Name = self.name_firewall_rule(
                                    'Internet',
                                    node.name, 'TCPv4_'+port+'_')

            sourceIPv4 = DimensionDataFirewallAddress(
                        any_ip=True,
                        ip_address=network.private_ipv4_range_address,
                        ip_prefix_size=network.private_ipv4_range_size,
                        port_begin=None,
                        port_end=None)

            destinationIPv4 = DimensionDataFirewallAddress(
                        any_ip=False,
                        ip_address=external_ip,
                        ip_prefix_size=None,
                        port_begin=port_begin,
                        port_end=port_end)

            ruleIPv4 = DimensionDataFirewallRule(
                            id=uuid4(),
                            action='ACCEPT_DECISIVELY',
                            name=ruleIPv4Name,
                            location=network.location,
                            network_domain=network.network_domain,
                            status='NORMAL',
                            ip_version='IPV4',
                            protocol='TCP',
                            enabled='true',
                            source=sourceIPv4,
                            destination=destinationIPv4)

            candidates[ruleIPv4Name] = ruleIPv4

        return candidates

    def _list_firewall_rules(self):
        """
        Lists all existing rules for the current domain
        """
        if len(self._cache_firewall_rules) < 1:
            self._cache_firewall_rules = self.region.ex_list_firewall_rules(
                self.get_network_domain(self.blueprint['domain']['name']))

        return self._cache_firewall_rules

    def _list_ipv4(self):
        """
        Lists public IPv4 addresses that have been assigned to a domain

        :returns: list of ``str``
           - the full list of public IPv4 addresses, or []
        """

        addresses = []

        while True:
            try:
                blocks = self.region.ex_list_public_ip_blocks(
                    self.get_network_domain(self.blueprint['domain']['name']))
                for block in blocks:
                    splitted = block.base_ip.split('.')
                    for ticker in xrange(int(block.size)):
                        addresses.append('.'.join(splitted))
                        splitted[3] = str(int(splitted[3])+1)

            except Exception as feedback:

                if 'RESOURCE_BUSY' in str(feedback):
                    time.sleep(10)
                    continue

                else:
                    logging.info("Unable to list IPv4 public addresses")
                    logging.info(str(feedback))
                    return []

            break

        return addresses

    def name_firewall_rule(self, source, destination, protocol):
        """
        Provides a name for a firewall rule

        :param source: name of the source network
        :type source: ``str``

        :param destination: name of the destination network
        :type destination: ``str``

        :param protocol: the protocol that will flow
        :type protocol: ``str``

        Use this function to ensure consistent naming across firewall rules.

        Example::

            >>>source='gigafox.control'
            >>>destination='gigafox.production'
            >>>protocol='IP'
            >>>domain.name_firewall_rule(source, destination, protocol)
            'plumbery.FlowIPFromGigafoxControlToGigafoxProduction'

        """

        source = ''.join(e for e in source.title() if e.isalnum())
        destination = ''.join(e for e in destination.title() if e.isalnum())

        if source == 'Internet':
            return "plumbery.{}{}".format(
                                                protocol,
                                                destination)

        else:
            return "plumbery.{}From{}To{}".format(
                                                protocol,
                                                source,
                                                destination)

    def _name_load_balancer(self, port):
        """
        Provides a name for the load balancer attached to a blueprint

        Use this function to ensure consistent naming across load balancers.

        """

        return 'Balancer.'+self.blueprint['target'].title()+'.'+str(port)

    def _release_ipv4(self):
        """
        Releases all public IPv4 addresses assigned to the blueprint

        """

        while True:
            try:
                blocks = self.region.ex_list_public_ip_blocks(
                    self.get_network_domain(self.blueprint['domain']['name']))

                if len(blocks) < 1:
                    return

                if self.plumbery.safeMode:
                    logging.info("Would have released public IPv4 addresses "
                                 "if not in safe mode")
                    return

                logging.info('Releasing public IPv4 addresses')

                for block in blocks:
                    self.region.ex_delete_public_ip_block(block)

                logging.info('- in progress')

            except Exception as feedback:

                if 'RESOURCE_BUSY' in str(feedback):
                    time.sleep(10)
                    continue

                elif 'HAS_DEPENDENCY' in str(feedback):
                    logging.info("- not now - stuff on it")

                elif 'RESOURCE_LOCKED' in str(feedback):
                    logging.info("- not now - locked")

                else:
                    logging.info("- unable to release IPv4 public addresses ")
                    logging.info(str(feedback))

            break

    def _remove_from_balancer(self, node):
        logging.info("Removing '{}' from load balancer".format(node.name))

    def _reserve_ipv4(self):
        """
        Reserves public addresses

        This function looks at current IPv4 addresses reserved for the
        target network domain, and adds more if needed.

        Example to reserve 8 IPv4 addresses in the fittings plan::

          - redis:
              domain:
                name: myVDC
                ipv4: 8

        """

        if 'ipv4' in self.blueprint['domain']:
            count = self.blueprint['domain']['ipv4']
        else:
            count = 2

        if count < 2 or count > 128:
            logging.info("Invalid count of requested IPv4 public addresses")
            return False

        actual = len(self._list_ipv4())
        if actual >= count:
            return True

        if self.plumbery.safeMode:
            logging.info("Would have reserved {} public IPv4 addresses "
                         "if not in safe mode".format(count-actual))
            return True

        logging.info('Reserving additional public IPv4 addresses')

        while actual < count:
            try:
                block = self.region.ex_add_public_ip_block_to_network_domain(
                    self.get_network_domain(self.blueprint['domain']['name']))
                actual += block.size
                logging.debug("- reserved {} addresses".format(block.size))

            except Exception as feedback:

                if 'RESOURCE_BUSY' in str(feedback):
                    time.sleep(10)
                    continue

                elif 'RESOURCE_LOCKED' in str(feedback):
                    logging.info("- not now - locked")
                    return False

                # compensate for bug in Libcloud driver
                elif 'RESOURCE_NOT_FOUND' in str(feedback):
                    actual += 2
                    continue

                else:
                    logging.info("- unable to reserve IPv4 public addresses")
                    logging.info(str(feedback))
                    return False

        logging.info("- reserved {} addresses in total".format(actual))

    def _update_ipv6(self, network, region=None):
        """
        Retrieves the ipv6 address for this network

        This is a hack. Code here should really go to the Libcloud driver in
        libcloud.compute.drivers.dimensiondata.py _to_vlan()

        """

        if region is None:
            region = self.region

        try:
            element = region.connection.request_with_orgId_api_2(
                'network/vlan/%s' % network.id).object

            ip_range = element.find(fixxpath('ipv6Range', TYPES_URN))

            network.ipv6_range_address = ip_range.get('address')
            network.ipv6_range_size = str(ip_range.get('prefixSize'))

        except Exception as feedback:

            if 'RESOURCE_NOT_FOUND' in str(feedback):
                network.ipv6_range_address = ''
                network.ipv6_range_size = ''

            else:
                logging.info("Error: unable to retrieve IPv6 addresses ")
                logging.info(str(feedback))
