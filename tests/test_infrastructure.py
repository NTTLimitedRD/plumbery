#!/usr/bin/env python

"""
Tests for `domain` module.
"""

import unittest

from plumbery.infrastructure import PlumberyInfrastructure


class FakeDomain:

    name = 'fake'
    id = 123


class FakeNetwork:

    name = 'fake'
    id = 123


class FakeRegion:

    def __call__(self, *args, **kwargs):
        return FakeRegion()

    def ex_create_network_domain(self, location, name, service_plan, description):
        return FakeDomain()

    def ex_create_vlan(self, network_domain, name, private_ipv4_base_address, description):
        return FakeNetwork()

    def ex_get_location_by_id(self, id):
        return None

    def ex_get_network_domain(self, location, network_domain):
        return []

    def ex_get_vlan(self, vlan_id):
        return FakeNetwork()

    def ex_list_nat_rules(self, domain):
        return []

    def ex_list_network_domains(self, location):
        return [FakeDomain()]

    def ex_list_vlans(self, location):
        return [FakeNetwork()]

    def ex_wait_for_state(self, state, func, poll_interval=2, timeout=60, *args, **kwargs):
        return []


class FakePlumbery:

    safeMode = False
    provider = FakeRegion()

    def get_user_name(self):
        return 'fake'

    def get_user_password(self):
        return 'fake'


class FakeFacility:

    plumbery = FakePlumbery()

    region = FakeRegion()

    location = 1

    _cache_network_domains = []
    _cache_vlans = []

fakeBluePrint = {'domain': {'name': 'fake',
                            'service': 'ADVANCED',
                            'description': '#vdc1'},
                'ethernet': {'name': 'fake',
                            'subnet': '10.0.10.0',
                            'description': '#vdc1'}}


class TestPlumberyInfrastructure(unittest.TestCase):

    def setUp(self):
        facility = FakeFacility()
        self.infrastructure = PlumberyInfrastructure(facility=facility)

    def tearDown(self):
        self.infrastructure = None

    def test_build(self):
        self.infrastructure.build(fakeBluePrint)

    def test_get_container(self):
        container = self.infrastructure.get_container(fakeBluePrint)
        self.assertEqual(container.domain.name, 'fake')
        self.assertEqual(container.network.name, 'fake')

    def test_get_ethernet(self):
        self.infrastructure.get_ethernet('MyNetwork')
        self.infrastructure.get_ethernet(['EU6', 'MyNetwork'])
        self.infrastructure.get_ethernet(['dd-eu', 'EU6', 'MyNetwork'])

    def test_get_ipv4(self):
        self.infrastructure.blueprint = fakeBluePrint
        self.infrastructure._get_ipv4()

    def test_get_network_domain(self):
        self.infrastructure.blueprint = fakeBluePrint
        self.infrastructure.get_network_domain('fake')

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
