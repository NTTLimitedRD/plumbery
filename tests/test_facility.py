#!/usr/bin/env python

"""
Tests for `facility` module.
"""

import os
import sys
import unittest

from plumbery.engine import PlumberyBlueprints
from plumbery.facility import PlumberyFacility


class FakeImage:

    name = 'RedHat 6 64-bit 4 CPU'

class FakeLocation:

    id = 'EU7'
    name = 'data centre in Amsterdam'
    country = 'Netherlands'


class FakePlumbery:

    userName = 'n'
    userPassword = 'p'
    safeMode = False
    sharedSecret = 's'

    def driver(self, name, password, region):
        return FakeRegion()


class FakeNode:

    name = 'stackstorm'
    extra = {'datacenterId': 'EU7'}


class FakeRegion:

    def create_node(self, name, image, auth, ex_network_domain, ex_vlan, ex_is_started, ex_description):
        return True

    def ex_create_network_domain(self, location, name, service_plan, description):
        return True

    def ex_create_vlan(self, network_domain, name, private_ipv4_base_address, description):
        return True

    def destroy_node(self, node):
        return True

    def ex_get_location_by_id(self, location):
        return FakeLocation()

    def ex_list_network_domains(self, location):
        return []

    def ex_list_vlans(self, location, network_domain):
        return []

    def ex_start_node(self, node):
        return True

    def ex_shutdown_graceful(self, node):
        return True

    def list_images(self, location):
        return [FakeImage()]

    def list_nodes(self):
        return [FakeNode()]


fakeFittings = {
    'regionId': 'dd-eu',
    'locationId': 'EU7',
    'blueprints': [{
            'fake': {
                    'domain': {
                            'name': 'VDC1',
                            'service': 'ADVANCED',
                            'description': 'fake'},
                    'ethernet': {
                            'name': 'vlan1',
                            'subnet': '10.0.10.0',
                            'description': 'fake'},
                     'nodes': [{
                            'stackstorm': {
                                    'description': 'fake',
                                    'appliance': 'RedHat 6 64-bit 4 CPU'
                                    }
                            }]
                    }
            }]
    }


class TestPlumberyFacility(unittest.TestCase):

    def setUp(self):
        plumbery = FakePlumbery()
        self.fittings = PlumberyBlueprints(**fakeFittings)
        self.facility = PlumberyFacility(plumbery=plumbery, fittings=self.fittings)

    def tearDown(self):
        self.facility = None

    def test_000(self):
        self.facility.build_all_blueprints()

    def test_001(self):
        self.facility.build_blueprint('fake')

    def test_010(self):
        self.facility.destroy_all_nodes()

    def test_011(self):
        self.facility.destroy_nodes('fake')

    def test_020(self):
        self.facility.focus()

    def test_030(self):
        self.facility.get_blueprint('fake')

    def test_031(self):
        self.facility.get_node('stackstorm')

    def test_040(self):
        self.facility.start_all_nodes()

    def test_041(self):
        self.facility.start_nodes('fake')

    def test_050(self):
        self.facility.stop_all_nodes()

    def test_051(self):
        self.facility.stop_nodes('fake')

    def test_099(self):
        self.facility.wait_and_tick(0)


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
