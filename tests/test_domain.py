#!/usr/bin/env python

"""
Tests for `domain` module.
"""

import unittest

from plumbery.domain import PlumberyDomain


class FakeDomain:

    id = 123


class FakeNetwork:

    id = 123


class FakePlumbery:

    safeMode = False


class FakeRegion:

    def ex_create_network_domain(self, location, name, service_plan, description):
        return FakeDomain()

    def ex_create_vlan(self, network_domain, name, private_ipv4_base_address, description):
        return FakeNetwork()

    def ex_get_network_domain(self, location, network_domain):
        return []

    def ex_get_vlan(self, vlan_id):
        return FakeNetwork()

    def ex_list_network_domains(self, location):
        return []

    def ex_list_vlans(self, location):
        return []

    def ex_wait_for_state(self, state, func, poll_interval=2, timeout=60, *args, **kwargs):
        return []


class FakeFacility:

    plumbery = FakePlumbery()

    region = FakeRegion()

    location = 1


fakeBluePrint = {'domain': {'name': 'fake',
                            'service': 'ADVANCED',
                            'description': '#vdc1'},
                'ethernet': {'name': 'fake',
                            'subnet': '10.0.10.0',
                            'description': '#vdc1'}}


class TestPlumberyDomain(unittest.TestCase):

    def setUp(self):
        facility = FakeFacility()
        self.domain = PlumberyDomain(facility=facility)

    def tearDown(self):
        self.domain = None

    def test_000(self):
        self.domain.build(fakeBluePrint)


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
