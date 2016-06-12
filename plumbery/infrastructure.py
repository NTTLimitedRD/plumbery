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

import time
from uuid import uuid4

try:
    from lxml import etree as ET
except ImportError:
    from xml.etree import ElementTree as ET

from libcloud.common.dimensiondata import DimensionDataFirewallRule
from libcloud.common.dimensiondata import DimensionDataFirewallAddress
from libcloud.common.dimensiondata import TYPES_URN

from libcloud.utils.xml import findall

from plumbery.terraform import Terraform
from plumbery.exception import PlumberyException
from plumbery.plogging import plogging

__all__ = ['PlumberyInfrastructure']


class PlumberyInfrastructure(object):
    """
    Infrastructure as code, for network and security

    :param facility: the underlying physical facility
    :type facility: :class:`plumbery.PlumberyFacility`

    This is an abstraction of a virtual data center. It is a secured
    container for multiple nodes.

    Example::

        from plumbery.infrastructure import PlumberyInfrastructure
        infrastructure = PlumberyInfrastructure(facility)
        infrastructure.build(blueprint)

    In this example an infrastructure is initialised at the given facility, and
    then it is asked to create pipes and plumbing described in the
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
        """A virtual data centre attached to a physical data centre"""

        # handle to parent parameters and functions
        self.facility = facility
        self.region = facility.region
        self.plumbery = facility.plumbery
        self.network = None
        self.domain = None
        self.terraform = Terraform(facility.plumbery.working_directory)

        self._cache_remote_vlan = []
        self._cache_offshore_vlan = []
        self._cache_firewall_rules = []
        self._cache_listeners = None
        self._cache_pools = None

        self._network_domains_already_built = []
        self._vlans_already_built = []

    def get_region_id(self):
        return self.facility.get_setting('regionId')

    def get_default(self, label, default=None):
        """
        Retrieves default value for a given name

        """

        value = self.facility.get_setting(label)
        if value is not None:
            return value
        return default

    def get_container(self, blueprint):
        """
        Retrieves a domain and a network attached to a blueprint

        :param blueprint: the various attributes of the target fittings
        :type blueprint: ``dict``

        :return: the infrastructure associated to the provided blueprint
        :rtype: :class:`plumbery.PlumberyInfrastructure` or `None``

        The returned object has at least a network domain and an Ethernet
        network, like in the following example::

            >>>container = infrastructure.get_container(blueprint)
            >>>print(container.domain.name)
            ...
            >>>print(container.network.name)
            ...

        """
        target = PlumberyInfrastructure(self.facility)

        target.blueprint = blueprint

        if ('domain' not in blueprint
                or type(blueprint['domain']) is not dict):

            raise PlumberyException(
                "Error: no network domain has been defined "
                "for the blueprint '{}'!".format(blueprint['target']))

        if ('ethernet' not in blueprint
                or type(blueprint['ethernet']) is not dict):

            raise PlumberyException(
                "Error: no ethernet network has been defined "
                "for the blueprint '{}'!".format(blueprint['target']))

        domainName = blueprint['domain']['name']
        target.domain = self.get_network_domain(domainName)

        networkName = blueprint['ethernet']['name']
        target.network = self.get_ethernet(networkName)

        return target

    def get_network_domain(self, name):
        """
        Retrieves a network domain by name

        :param name: name of the target network domain
        :type name: ``str``

        """

        if len(self.facility._cache_network_domains) < 1:
            plogging.debug("Listing network domains")
            self.facility._cache_network_domains = \
                self.region.ex_list_network_domains(
                    self.facility.get_location_id())
            plogging.debug("- found {} network domains"
                          .format(len(self.facility._cache_network_domains)))

        for domain in self.facility._cache_network_domains:
            if domain.name == name:
                return domain

        return None

    def get_ethernet(self, path):
        """
        Retrieves an Ethernet network by name

        :param path: the name of the target Ethernet network
        :type path: ``str`` or ``list``of ``str``

        :return: an instance of an Ethernet network
        :rtype: :class:`VLAN` or ``None``

        This function searches firstly at the current facility. If the
        name is a complete path to a remote network, then plumbery looks
        there. If a different region is provided, then authentication is done
        against the related endpoint.

        For example if ``MyNetwork`` has been defined in a data centre in
        Europe::

            >>>infrastructure.get_ethernet('MyNetwork')
            >>>infrastructure.get_ethernet(['EU6', 'MyNetwork'])
            Looking for remote Ethernet network 'EU6::MyNetwork'
            - found it
            >>>infrastructure.get_ethernet(['dd-eu', 'EU6', 'MyNetwork'])
            Looking for offshore Ethernet network 'dd-eu::EU6::MyNetwork'
            - found it

        """

        if isinstance(path, str):
            path = path.split('::')

        if len(path) == 2:  # force offshore lookup if needed
            target_region = self.facility.get_region(path[0])
            if target_region != self.facility.get_region():
                path.insert(0, target_region)

        if len(path) == 1:  # local name

            if len(self.facility._cache_vlans) < 1:
                plogging.debug("Listing Ethernet networks")
                self.facility._cache_vlans = self.region.ex_list_vlans(
                    location=self.facility.get_location_id())
                plogging.debug("- found {} Ethernet networks"
                              .format(len(self.facility._cache_vlans)))

            for network in self.facility._cache_vlans:
                if network.name == path[0]:
                    return network

        elif len(path) == 2:  # different location, same region

            if (len(self._cache_remote_vlan) == 3
                    and self._cache_remote_vlan[0] == path[0]
                    and self._cache_remote_vlan[1] == path[1]):

                return self._cache_remote_vlan[2]

            plogging.info("Looking for remote Ethernet network '%s'",
                         '::'.join(path))

            try:
                remoteLocation = self.region.ex_get_location_by_id(path[0])
            except IndexError:
                plogging.info("- '%s' is unknown", path[0])
                return None

            vlans = self.region.ex_list_vlans(location=remoteLocation)
            for network in vlans:
                if network.name == path[1]:
                    self._cache_remote_vlan += path
                    self._cache_remote_vlan.append(network)
                    plogging.info("- found it")
                    return network

            plogging.info("- not found")

        elif len(path) == 3:  # other region

            if (len(self._cache_offshore_vlan) == 4
                    and self._cache_offshore_vlan[0] == path[0]
                    and self._cache_offshore_vlan[1] == path[1]
                    and self._cache_offshore_vlan[2] == path[2]):

                return self._cache_offshore_vlan[3]

            plogging.info("Looking for offshore Ethernet network '{}'"
                         .format('::'.join(path)))

            offshore = self.plumbery.get_compute_driver(region=path[0])

            try:
                remoteLocation = offshore.ex_get_location_by_id(path[1])
            except IndexError:
                plogging.info("- '{}' is unknown".format(path[1]))
                return None

            vlans = offshore.ex_list_vlans(location=remoteLocation)
            for network in vlans:
                if network.name == path[2]:
                    self._cache_offshore_vlan += path
                    self._cache_offshore_vlan.append(network)
                    plogging.info("- found it")
                    return network

            plogging.info("- not found")

        return None

    def build(self, blueprint):
        """
        Creates the infrastructure for one blueprint

        :param blueprint: the various attributes of the target fittings
        :type blueprint: ``dict``

        :return: ``True`` if the network has been created or is already there,
            ``False`` otherwise
        :rtype: ``bool``

        :raises: :class:`plumbery.PlumberyException`
            - if some unrecoverable error occurs

        This function is looking at all fittings in the blueprint except the
        nodes. This is including:

        * a network domain
        * one Ethernet network
        * eventually, several public IPv4 addresses
        * address translation rules to private IPv4 addresses
        * firewall rules

        In safe mode, the function will stop on any missing component since
        it is not in a position to add fittings, and return ``False``.
        If all components already exist then the funciton will return ``True``.

        """

        self.blueprint = blueprint

        plogging.debug("Building infrastructure of blueprint '{}'".format(
            blueprint['target']))

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
            plogging.info("Creating network domain '{}'".format(domainName))
            plogging.info("- already there")

        elif self.plumbery.safeMode:
            plogging.info("Creating network domain '{}'".format(domainName))
            plogging.info("- skipped - safe mode")
            plogging.info("Creating Ethernet network '{}'"
                         .format(networkName))
            plogging.info("- skipped - safe mode")
            return False

        else:
            plogging.info("Creating network domain '{}'".format(domainName))

            # the description attribute is a smart way to tag resources
            description = '#plumbery'
            if 'description' in blueprint['domain']:
                description = blueprint['domain']['description']+' #plumbery'

            # level of service
            service = 'ESSENTIALS'
            if 'service' in blueprint['domain']:
                service = blueprint['domain']['service'].upper()

            while True:
                try:
                    self.domain = self.region.ex_create_network_domain(
                        location=self.facility.location,
                        name=domainName,
                        service_plan=service,
                        description=description)
                    plogging.info("- in progress")

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
                        plogging.info("- operation not supported")
                        return False

                    elif 'RESOURCE_LOCKED' in str(feedback):
                        plogging.info("- not now - locked")
                        return False

                    else:
                        plogging.info("- unable to create network domain")
                        plogging.error(str(feedback))
                        return False

                break

        self.network = self.get_ethernet(networkName)
        if self.network is not None:
            plogging.info("Creating Ethernet network '{}'"
                         .format(networkName))
            plogging.info("- already there")

        elif self.plumbery.safeMode:
            plogging.info("Creating Ethernet network '{}'"
                         .format(networkName))
            plogging.info("- skipped - safe mode")
            return False

        else:
            plogging.info("Creating Ethernet network '{}'"
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
                    plogging.info("- in progress")

                    # prevent locks in xops
                    self.region.ex_wait_for_state(
                        'NORMAL',
                        self.region.ex_get_vlan,
                        poll_interval=5, timeout=1200,
                        vlan_id=self.network.id)

                    self.facility._cache_vlans.append(self.network)

                except Exception as feedback:

                    if 'RESOURCE_BUSY' in str(feedback):
                        time.sleep(10)
                        continue

                    elif 'NAME_NOT_UNIQUE' in str(feedback):
                        plogging.info("- not possible "
                                     "- network already exists elsewhere")

                    elif 'IP_ADDRESS_NOT_UNIQUE' in str(feedback):
                        plogging.info("- not possible "
                                     "- subnet is used elsewhere")

                    elif 'RESOURCE_LOCKED' in str(feedback):
                        plogging.info("- not now - locked")
                        return False

                    else:
                        plogging.info("- unable to create Ethernet network")
                        plogging.error(str(feedback))
                        return False

                break

        if 'multicloud' in blueprint                                      \
           and isinstance(blueprint['multicloud'], dict):
            plogging.info("Starting multicloud deployment")
            self.terraform.build(blueprint['multicloud'])

        return True

    def destroy_blueprint(self, blueprint):
        """
        Destroys network and security elements of a blueprint

        :param blueprint: the various attributes of the target fittings
        :type blueprint: ``dict``

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

        if ('domain' not in blueprint
                or type(blueprint['domain']) is not dict):

            raise PlumberyException(
                "Error: no network domain has been defined "
                "for the blueprint '{}'!".format(blueprint['target']))

        if ('ethernet' not in blueprint
                or type(blueprint['ethernet']) is not dict):

            raise PlumberyException(
                "Error: no ethernet network has been defined "
                "for the blueprint '{}'!".format(blueprint['target']))

        domainName = blueprint['domain']['name']
        networkName = blueprint['ethernet']['name']

        domain = self.get_network_domain(domainName)
        if domain is None:
            plogging.info("Destroying Ethernet network '{}'"
                         .format(networkName))
            plogging.info("- not found")
            plogging.info("Destroying network domain '{}'".format(domainName))
            plogging.info("- not found")
            return

        self._destroy_firewall_rules()

        self._destroy_balancer()

        self._release_ipv4()

        plogging.info("Destroying Ethernet network '{}'".format(networkName))

        network = self.get_ethernet(networkName)
        if network is None:
            plogging.info("- not found")

        elif ('destroy' in blueprint['ethernet']
                and blueprint['ethernet']['destroy'] == 'never'):
            plogging.info("- this network can never be destroyed")

        elif self.plumbery.safeMode:
            plogging.info("- skipped - safe mode")

        else:

            retry = True
            while True:
                try:
                    self.region.ex_delete_vlan(vlan=network)
                    plogging.info("- in progress")

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
                        plogging.info("- not found")

                    elif 'HAS_DEPENDENCY' in str(feedback):

                        # give time to ensure nodes have been deleted
                        if retry:
                            retry = False
                            time.sleep(30)
                            continue

                        plogging.info("- not now - stuff on it")
                        return

                    elif 'RESOURCE_LOCKED' in str(feedback):
                        plogging.info("- not now - locked")
                        plogging.info(feedback)
                        return

                    else:
                        plogging.info("- unable to destroy Ethernet network")
                        plogging.error(str(feedback))
                        return

                break

        plogging.info("Destroying network domain '{}'".format(domainName))

        if 'multicloud' in blueprint                                      \
           and isinstance(blueprint['multicloud'], dict):
            plogging.info("Destroying multicloud deployment")
            self.terraform.destroy(blueprint['multicloud'], safe=self.plumbery.safeMode)

        if self.plumbery.safeMode:
            plogging.info("- skipped - safe mode")
            return

        while True:
            try:
                self.region.ex_delete_network_domain(network_domain=domain)
                plogging.info("- in progress")

            except Exception as feedback:

                if 'RESOURCE_BUSY' in str(feedback):
                    time.sleep(10)
                    continue

                elif 'RESOURCE_NOT_FOUND' in str(feedback):
                    plogging.info("- not found")

                elif 'HAS_DEPENDENCY' in str(feedback):
                    plogging.info("- not now - stuff on it")
                    return

                elif 'RESOURCE_LOCKED' in str(feedback):
                    plogging.info("- not now - locked")
                    return

                else:
                    plogging.info("- unable to destroy Ethernet network")
                    plogging.error(str(feedback))
                    return

            break

    def _build_balancer(self):
        """
        Adds a load balancer for nodes in the blueprint

        Example in the fittings plan::

          - web:
              domain: *vdc1
              ethernet: *data
              nodes:
                - apache[10..19]
              listeners:
                - http:
                    port: 80
                    protocol: http
                - https:
                    port: 443
                    protocol: http
              balancer:
                algorithm: round_robin

        In this example, the load balancer is configured to accept web traffic
        and to distribute the workload across multiple web engines.

        One listener is configured for regular http protocol on port 80. The
        other listener is for secured web protocol, aka, https, on port 443.

        The algorithm used by default is ``round_robin``. This parameter
        can take any value among followings:

        * ``random``
        * ``round_robin``
        * ``least_connections``
        * ``weighted_round_robin``
        * ``weighted_least_connections``
        * ``shortest_response``
        * ``persistent_ip``

        """

        if 'listeners' not in self.blueprint:
            return True

        domain = self.get_network_domain(self.blueprint['domain']['name'])
        driver = self.plumbery.get_balancer_driver(self.get_region_id())
        driver.ex_set_current_network_domain(domain.id)

        pool = self._get_pool()

        if pool is None:

            if 'balancer' in self.blueprint:
                settings = self.blueprint['balancer']
                if not isinstance(settings, dict):
                    settings = {}
            else:
                settings = {}

            name = self._name_pool()

            if 'algorithm' in settings:
                algorithm = settings['algorithm'].lower()
            else:
                algorithm = 'round_robin'

            algorithms = [
                'random',
                'round_robin',
                'least_connections',
                'weighted_round_robin',
                'weighted_least_connections',
                'shortest_response',
                'persistent_ip']

            if algorithm not in algorithms:
                raise PlumberyException(
                    "Error: unknown algorithm has been defined "
                    "for the pool '{}'!".format(name))

            plogging.info("Creating pool '{}'".format(name))

            if self.plumbery.safeMode:
                plogging.info("- skipped - safe mode")

            else:
                try:
                    pool = driver.ex_create_pool(
                        network_domain_id=domain.id,
                        name=name,
                        balancer_method=algorithm,
                        ex_description="#plumbery",
                        health_monitors=None,
                        service_down_action='NONE',
                        slow_ramp_time=30)

                    if self._cache_pools is None:
                        self._cache_pools = []
                    self._cache_pools.append(pool)

                    plogging.info("- in progress")

                except Exception as feedback:

                    if 'NAME_NOT_UNIQUE' in str(feedback):
                        plogging.info("- already there")

                    else:
                        plogging.info("- unable to create pool")
                        plogging.error(str(feedback))

        for item in self.blueprint['listeners']:

            if isinstance(item, dict):
                label = list(item)[0]
                settings = item[label]
            else:
                label = str(item)
                settings = {}

            name = self.name_listener(label, settings)

            if self._get_listener(name):
                plogging.info("Creating listener '{}'".format(name))
                plogging.info("- already there")
                continue

            if 'port' in settings:
                port = settings['port']
            else:
                port = '80'

            port = int(port)
            if port < 1 or port > 65535:
                raise PlumberyException(
                    "Error: invalid port has been defined "
                    "for the listener '{}'!".format(label))

            if 'protocol' in settings:
                protocol = settings['protocol']
            else:
                protocol = 'http'

            protocols = ['http', 'https', 'tcp', 'udp']

            if protocol not in protocols:
                raise PlumberyException(
                    "Error: unknown protocol has been defined "
                    "for the listener '{}'!".format(label))

            plogging.info("Creating listener '{}'".format(name))

            if self.plumbery.safeMode:
                plogging.info("- skipped - safe mode")
                continue

            try:
                listener = driver.ex_create_virtual_listener(
                    network_domain_id=domain.id,
                    name=name,
                    ex_description="#plumbery",
                    port=port,
                    pool=pool,
                    persistence_profile=None,
                    fallback_persistence_profile=None,
                    irule=None,
                    protocol='TCP',
                    connection_limit=25000,
                    connection_rate_limit=2000,
                    source_port_preservation='PRESERVE')

                if self._cache_listeners is None:
                    self._cache_listeners = []
                self._cache_listeners.append(listener)

                plogging.info("- in progress")

            except Exception as feedback:

                if 'NAME_NOT_UNIQUE' in str(feedback):
                    plogging.info("- already there")

                elif 'NO_IP_ADDRESS_AVAILABLE' in str(feedback):
                    plogging.info("- no more ipv4 address available "
                                 "-- assign more")

                else:
                    plogging.info("- unable to create listener")
                    plogging.error(str(feedback))

        return True

    def _destroy_balancer(self):
        """
        Destroys load balancer

        """

        if 'listeners' not in self.blueprint:
            return True

        domain = self.get_network_domain(self.blueprint['domain']['name'])
        driver = self.plumbery.get_balancer_driver(self.get_region_id())
        driver.ex_set_current_network_domain(domain.id)

        for item in self.blueprint['listeners']:

            if isinstance(item, dict):
                label = list(item)[0]
                settings = item[label]
            else:
                label = str(item)
                settings = {}

            name = self.name_listener(label, settings)

            listener = self._get_listener(name)

            plogging.info("Destroying listener '{}'".format(name))

            if listener is None:
                plogging.info("- not found")
                continue

            if self.plumbery.safeMode:
                plogging.info("- skipped - safe mode")
                continue

            try:
                driver.destroy_balancer(listener)
                plogging.info("- in progress")

            except Exception as feedback:

                if 'NOT_FOUND' in str(feedback):
                    plogging.info("- not found")

                else:
                    plogging.info("- unable to destroy listener")
                    plogging.error(str(feedback))

        pool = self._get_pool()

        plogging.info("Destroying pool '{}'".format(self._name_pool()))

        if pool is None:
            plogging.info("- not found")

        elif self.plumbery.safeMode:
            plogging.info("- skipped - safe mode")

        else:
            try:
                driver.ex_destroy_pool(pool)
                plogging.info("- in progress")

            except Exception as feedback:

                if 'NAME_NOT_UNIQUE' in str(feedback):
                    plogging.info("- already there")

                else:
                    plogging.info("- unable to destroy pool")
                    plogging.error(str(feedback))

    def name_listener(self, label, settings={}):
        return self.blueprint['target']                 \
            + '_' + self.facility.get_location_id().lower()      \
            + '.' + label + '.listener'

    def _get_listener(self, name):
        """
        Retrieves a listener attached to this blueprint

        """

        domain = self.get_network_domain(self.blueprint['domain']['name'])
        driver = self.plumbery.get_balancer_driver(self.get_region_id())
        if driver is None:
            return None
        if domain is None:
            return None
        driver.ex_set_current_network_domain(domain.id)

        if self._cache_listeners is None:
            plogging.info("Listing listeners")
            self._cache_listeners = driver.list_balancers()
            plogging.info("- found {} listeners"
                         .format(len(self._cache_listeners)))

        for listener in self._cache_listeners:

            if listener.name.lower() == name.lower():
                return listener

        return None

    def _name_pool(self):
        return self.blueprint['target']                     \
            + '_' + self.facility.get_location_id().lower() + '.pool'

    def _get_pool(self):
        """
        Retrieves the pool attached to this blueprint

        """

        if 'listeners' not in self.blueprint:
            return None

        domain = self.get_network_domain(self.blueprint['domain']['name'])
        driver = self.plumbery.get_balancer_driver(self.get_region_id())
        driver.ex_set_current_network_domain(domain.id)

        name = self._name_pool()

        if self._cache_pools is None:
            plogging.info("Listing pools")
            self._cache_pools = driver.ex_get_pools()
            plogging.info("- found {} pools".format(len(self._cache_pools)))

        for pool in self._cache_pools:

            if pool.name.lower() == name.lower():
                return pool

        return None

    def name_member(self, node):
        return node.name+'.plumbery'

    def _add_to_pool(self, node):
        """
        Makes a node a new member of the pool

        """

        if 'listeners' not in self.blueprint:
            return

        pool = self._get_pool()
        if pool is None:
            return

        domain = self.get_network_domain(self.blueprint['domain']['name'])
        driver = self.plumbery.get_balancer_driver(self.get_region_id())
        driver.ex_set_current_network_domain(domain.id)

        plogging.info("Adding '{}' to pool '{}'".format(node.name, pool.name))

        name = self.name_member(node)
        members = driver.ex_get_pool_members(pool.id)
        for member in members:

            if member.name == name:
                plogging.info("- already there")
                return

        if self.plumbery.safeMode:
            plogging.info("- skipped - safe mode")
            return

        try:
            member = driver.ex_create_node(
                network_domain_id=domain.id,
                name=name,
                ip=node.private_ips[0],
                ex_description='#plumbery')

            driver.ex_create_pool_member(
                pool=pool,
                node=member,
                port='*padding*')

            plogging.info("- in progress")

        except Exception as feedback:

            if 'NAME_NOT_UNIQUE' in str(feedback):
                plogging.info("- already there")
                plogging.error(str(feedback))

            else:
                plogging.info("- unable to add to pool")
                plogging.error(str(feedback))

    def _remove_from_pool(self, node):
        """
        Removes a node from the pool

        """

        if 'listeners' not in self.blueprint:
            return

        domain = self.get_network_domain(self.blueprint['domain']['name'])
        driver = self.plumbery.get_balancer_driver(self.get_region_id())
        driver.ex_set_current_network_domain(domain.id)

        pool = self._get_pool()
        if pool is not None:

            plogging.info("Removing '{}' from pool '{}'".format(
                node.name,
                pool.name))

            members = driver.ex_get_pool_members(pool.id)

            found = False
            for member in members:

                if member.name == self.name_member(node):

                    if self.plumbery.safeMode:
                        plogging.info("- skipped - safe mode")
                        return

                    try:
                        driver.balancer_detach_member(
                            balancer='*unused*',
                            member=member)
                        plogging.info("- in progress")

                    except Exception as feedback:

                        if 'RESOURCE_NOT_FOUND' in str(feedback):
                            plogging.info("- not found")

                        else:
                            plogging.info("- unable to remove from pool")
                            plogging.error(str(feedback))

                    found = True
                    break

            if not found:
                plogging.info("- already there")

        try:
            plogging.info("Destroying membership of '{}'".format(node.name))

            members = driver.ex_get_nodes()
            for member in members:
                if member.name == self.name_member(node):
                    driver.ex_destroy_node(member.id)
                    break

            plogging.info("- in progress")

        except Exception as feedback:

            if 'RESOURCE_NOT_FOUND' in str(feedback):
                plogging.info("- not found")

            else:
                plogging.info("- unable to destroy membership")
                plogging.error(str(feedback))

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

                plogging.info("Detaching node '{}' from the internet"
                             .format(node.name))

                while True:
                    try:
                        self.region.ex_delete_nat_rule(rule)
                        plogging.info("- in progress")

                    except Exception as feedback:
                        if 'RESOURCE_BUSY' in str(feedback):
                            time.sleep(10)
                            continue

                        elif 'RESOURCE_LOCKED' in str(feedback):
                            plogging.info("- not now - locked")
                            return

                        else:
                            plogging.info("- unable to remove "
                                         "address translation")
                            plogging.error(str(feedback))

                    break

        for rule in self._list_firewall_rules():

            if rule.name.lower().startswith(node.name.lower()):

                plogging.info("Destroying firewall rule '{}'"
                             .format(rule.name))

                if self.plumbery.safeMode:
                    plogging.info("- skipped - safe mode")

                else:
                    self.region.ex_delete_firewall_rule(rule)
                    plogging.info("- in progress")

    def _get_ipv4(self):
        """
        Provides a free public IPv4 if possible

        This function looks at current IPv4 addresses reserved for the
        target network domain, and adds more if needed.

        Example to reserve 8 IPv4 addresses in the fittings plan::

          - redis:
              domain:
                name: myVDC
                ipv4: 8

        If the directive `auto` is used, then plumbery do not check the
        maximum number of addresses that can be provided.
        """

        domain = self.get_network_domain(self.blueprint['domain']['name'])
        if domain is None:
            return None

        addresses = self._list_ipv4()
        if len(addresses) > 1:

            for rule in self.region.ex_list_nat_rules(domain):
                addresses.remove(rule.external_ip)

            if 'balancer' in self.blueprint:
                addresses.pop(0)

        if len(addresses) > 0:
            return addresses[0]

        actual = len(self._list_ipv4())

        if 'ipv4' in self.blueprint['domain']:
            count = self.blueprint['domain']['ipv4']
        else:
            count = self.get_default('ipv4', 2)

        if str(count).lower() == 'auto':
            count = actual + 2

        if count < 2 or count > 128:
            logging.warning("Invalid count of requested IPv4 public addresses")
            return None

        if actual >= count:
            return None

        plogging.info('Reserving additional public IPv4 addresses')

        if self.plumbery.safeMode:
            plogging.info("- skipped - safe mode")
            return None

        count = actual + 2
        while actual < count:
            try:
                block = self.region.ex_add_public_ip_block_to_network_domain(
                    self.get_network_domain(self.blueprint['domain']['name']))
                actual += int(block.size)
                plogging.info("- reserved {} addresses"
                             .format(int(block.size)))
                return block.base_ip

            except Exception as feedback:

                if 'RESOURCE_BUSY' in str(feedback):
                    time.sleep(10)
                    continue

                elif 'RESOURCE_LOCKED' in str(feedback):
                    plogging.info("- not now - locked")
                    return None

                # compensate for bug in Libcloud driver
                elif 'RESOURCE_NOT_FOUND' in str(feedback):
                    actual += 2
                    continue

                else:
                    plogging.info("- unable to reserve IPv4 public addresses")
                    plogging.error(str(feedback))
                    return None

    def _list_ipv4(self):
        """
        Lists public IPv4 addresses that have been assigned to a domain

        :return: the full list of public IPv4 addresses assigned to the domain
        :rtype: ``list`` of ``str`` or ``[]``

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
                    plogging.info("Unable to list IPv4 public addresses")
                    plogging.error(str(feedback))
                    return []

            break

        return addresses

    def _release_ipv4(self):
        """
        Releases public IPv4 addresses assigned to the blueprint

        """

        domain = self.get_network_domain(self.blueprint['domain']['name'])
        if len(self.region.ex_list_nat_rules(domain)) > 0:
            return

        blocks = self.region.ex_list_public_ip_blocks(
            self.get_network_domain(self.blueprint['domain']['name']))

        if len(blocks) < 1:
            return

        plogging.info('Releasing public IPv4 addresses')

        if self.plumbery.safeMode:
            plogging.info("- skipped - safe mode")
            return

        for block in blocks:
            while True:
                try:
                    self.region.ex_delete_public_ip_block(block)
                    plogging.info('- in progress')

                except Exception as feedback:

                    if 'RESOURCE_BUSY' in str(feedback):
                        time.sleep(10)
                        continue

                    elif 'HAS_DEPENDENCY' in str(feedback):
                        plogging.info("- not now - stuff at '{}' and beyond"
                                     .format(block.base_ip))

                    elif 'RESOURCE_LOCKED' in str(feedback):
                        plogging.info("- not now - locked")

                    else:
                        plogging.info("- unable to release "
                                     "IPv4 public addresses ")
                        plogging.error(str(feedback))

                break

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
        if destination is None:
            return True

        destinationIPv4 = DimensionDataFirewallAddress(
            any_ip=False,
            ip_address=destination.private_ipv4_range_address,
            ip_prefix_size=destination.private_ipv4_range_size,
            port_begin=None,
            port_end=None,
            address_list_id=None,
            port_list_id=None)

        destinationIPv6 = DimensionDataFirewallAddress(
            any_ip=False,
            ip_address=destination.ipv6_range_address,
            ip_prefix_size=destination.ipv6_range_size,
            port_begin=None,
            port_end=None,
            address_list_id=None,
            port_list_id=None)

        for item in self.blueprint['ethernet']['accept']:

            if isinstance(item, dict):
                label = list(item)[0]
            else:
                label = str(item)

            source = self.get_ethernet(label)
            if source is None:
                plogging.debug("Source network '{}' is unknown".format(label))
                continue

            # avoid name collisions across local, remote and off-shore networks
            tokens = label.split('::')
            while len(tokens) > 2:
                tokens.pop(0)
            source_name = '-'.join(tokens)

            ruleIPv4Name = self.name_firewall_rule(
                source_name, destination.name, 'IP')

            shouldCreateRuleIPv4 = True
            if source.location.name != destination.location.name:
                shouldCreateRuleIPv4 = False
            elif source.network_domain.name != destination.network_domain.name:
                shouldCreateRuleIPv4 = False

            ruleIPv6Name = self.name_firewall_rule(
                source_name, destination.name, 'IPv6')

            shouldCreateRuleIPv6 = True

            for rule in self._list_firewall_rules():

                if (shouldCreateRuleIPv4
                        and rule.name.lower() == ruleIPv4Name.lower()):

                    plogging.info("Creating firewall rule '{}'"
                                 .format(rule.name))
                    plogging.info("- already there")
                    shouldCreateRuleIPv4 = False
                    continue

                if (shouldCreateRuleIPv6
                        and rule.name.lower() == ruleIPv6Name.lower()):

                    plogging.info("Creating firewall rule '{}'"
                                 .format(rule.name))
                    plogging.info("- already there")
                    shouldCreateRuleIPv6 = False
                    continue

            if shouldCreateRuleIPv4:

                plogging.info("Creating firewall rule '{}'"
                             .format(ruleIPv4Name))

                if self.plumbery.safeMode:
                    plogging.info("- skipped - safe mode")

                else:

                    sourceIPv4 = DimensionDataFirewallAddress(
                        any_ip=False,
                        ip_address=source.private_ipv4_range_address,
                        ip_prefix_size=source.private_ipv4_range_size,
                        port_begin=None,
                        port_end=None,
                        address_list_id=None,
                        port_list_id=None)

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

                        plogging.info("- in progress")

                    except Exception as feedback:

                        if 'NAME_NOT_UNIQUE' in str(feedback):
                            plogging.info("- already there")

                        else:
                            plogging.info("- unable to create firewall rule")
                            plogging.error(str(feedback))

            if shouldCreateRuleIPv6:

                plogging.info("Creating firewall rule '{}'"
                             .format(ruleIPv6Name))

                if self.plumbery.safeMode:
                    plogging.info("- skipped - safe mode")

                else:

                    sourceIPv6 = DimensionDataFirewallAddress(
                        any_ip=False,
                        ip_address=source.ipv6_range_address,
                        ip_prefix_size=source.ipv6_range_size,
                        port_begin=None,
                        port_end=None,
                        address_list_id=None,
                        port_list_id=None)

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

                        plogging.info("- in progress")

                    except Exception as feedback:

                        if 'NAME_NOT_UNIQUE' in str(feedback):
                            plogging.info("- already there")

                        else:
                            plogging.info("- unable to create firewall rule")
                            plogging.error(str(feedback))

        ruleName = 'CCDEFAULT.DenyExternalInboundIPv6'
        for rule in self._list_firewall_rules():
            if rule.name.lower() == ruleName.lower():
                plogging.info("Disabling firewall rule '{}'".format(ruleName))

                try:
                    if rule.enabled:
                        self.region.ex_set_firewall_rule_state(rule, False)
                        plogging.info("- in progress")

                    else:
                        plogging.info("- already there")

                except Exception as feedback:
                    plogging.info("- unable to disable firewall rule")
                    plogging.error(str(feedback))

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
                label = list(item)[0]
            else:
                label = str(item)

            sourceLabel = label.split('::').pop()

            ruleIPv4Name = self.name_firewall_rule(
                sourceLabel, destinationLabel, 'IP')

            ruleIPv6Name = self.name_firewall_rule(
                sourceLabel, destinationLabel, 'IPv6')

            for rule in self._list_firewall_rules():

                if rule.name == ruleIPv4Name or rule.name == ruleIPv6Name:

                    plogging.info("Destroying firewall rule '{}'"
                                 .format(rule.name))

                    if self.plumbery.safeMode:
                        plogging.info("- skipped - safe mode")

                    else:
                        try:
                            self.region.ex_delete_firewall_rule(rule)
                            plogging.info("- in progress")

                        except Exception as feedback:

                            if 'RESOURCE_NOT_FOUND' in str(feedback):
                                plogging.info("- not found")

                            else:
                                plogging.info("- unable to destroy "
                                             "firewall rule")
                                plogging.error(str(feedback))

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

        source = ''.join(e for e in source.title()
                         if e.isalnum() or e == '_')
        destination = ''.join(e for e in destination.title()
                              if e.isalnum() or e == '_')

        if source == 'Internet':
            return "{}.{}.plumbery".format(destination, protocol)

        else:
            return "From{}To{}.{}.plumbery".format(source,
                                                   destination,
                                                   protocol)

    @classmethod
    def parse_firewall_port(cls, port):
        """
        Parses port definition for a firewall rule

        :param port: string definition of a target port
        :type port: ``str``

        :return: elements of the port definition

        This function analyses the provided string and returns
        a tuple that can be used for firewall configuration.

        Some examples:
        >>>container.parse_firewall_port('icmp')
        ('ICMP', 'any', None, None)
        >>>container.parse_firewall_port('tcp:80')
        ('TCP', '80', '80', None)
        >>>container.parse_firewall_port(':80')
        ('TCP', '80', '80', None)
        >>>container.parse_firewall_port('80')
        ('TCP', '80', '80', None)
        >>>container.parse_firewall_port('udp:137..138')
        ('UDP', '137..138', '137', '138')
        >>>container.parse_firewall_port('any')
        ('TCP', 'any', None, None)

        """

        protocols = ('ip', 'icmp', 'tcp', 'udp')

        tokens = port.lower().strip(':').split(':')
        if len(tokens) > 1:  # example: 'TCP:80'
            protocol = tokens[0].upper()
            port = tokens[1]

        elif tokens[0] in protocols:  # example: 'icmp'
            protocol = tokens[0].upper()
            port = 'any'

        else:  # example: '80'
            protocol = 'TCP'
            port = tokens[0]

        if protocol.lower() not in protocols:
            raise ValueError("'{}' is not a valid protocol"
                             .format(protocol))

        tokens = port.split('..')
        if len(tokens) == 1:
            if tokens[0].lower() == 'any':
                port_begin = None
            else:
                port_begin = tokens[0]
            port_end = None

        else:
            port_begin = tokens[0]
            port_end = tokens[1]

        return (protocol, port, port_begin, port_end)

    def _list_candidate_firewall_rules(self, node, ports=[]):
        """
        Lists rules that should apply to one node

        :param node: node that has to be reachable from the internet
        :type node: :class:`libcloud.common.Node`

        :param ports: the ports that have to be opened, or ``any``
        :type ports: a ``list`` of ``str``

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

            protocol, port, port_begin, port_end = \
                self.parse_firewall_port(port)

            ruleIPv4Name = self.name_firewall_rule(
                'Internet',
                node.name, protocol+'v4_'+port)

            sourceIPv4 = DimensionDataFirewallAddress(
                any_ip=True,
                ip_address=network.private_ipv4_range_address,
                ip_prefix_size=network.private_ipv4_range_size,
                port_begin=None,
                port_end=None,
                address_list_id=None,
                port_list_id=None)

            destinationIPv4 = DimensionDataFirewallAddress(
                any_ip=False,
                ip_address=external_ip,
                ip_prefix_size=None,
                port_begin=port_begin,
                port_end=port_end,
                address_list_id=None,
                port_list_id=None)

            ruleIPv4 = DimensionDataFirewallRule(
                id=uuid4(),
                action='ACCEPT_DECISIVELY',
                name=ruleIPv4Name,
                location=network.location,
                network_domain=network.network_domain,
                status='NORMAL',
                ip_version='IPV4',
                protocol=protocol,
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
