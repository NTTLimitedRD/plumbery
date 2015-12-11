#!/usr/bin/env python

"""
Tests for `facility` module.
"""

import unittest

from plumbery.engine import PlumberyFittings, PlumberyEngine
from plumbery.facility import PlumberyFacility

class FakeElement:

    def find(self, dummy):
        return {'ipv6': 'nuts'}

class FakeConnection:

    object = FakeElement()

    def request_with_orgId_api_2(self, dummy):
        return self

class FakeDomain:

    id = 123

class FakeImage:

    name = 'RedHat 6 64-bit 4 CPU'


class FakeLocation:

    id = 'EU7'
    name = 'data centre in Amsterdam'
    country = 'Netherlands'


class FakeNetwork:

    id = 123


class FakeNode:

    id = 123
    name = 'stackstorm'
    extra = {'datacenterId': 'EU7'}


class FakeRegion:

    connection = FakeConnection()

    def create_node(self, name, image, auth, ex_network_domain, ex_vlan, ex_is_started, ex_description):
        return True

    def ex_create_network_domain(self, location, name, service_plan, description):
        return FakeDomain()

    def ex_create_vlan(self, network_domain, name, private_ipv4_base_address, description):
        return FakeNetwork()

    def ex_get_location_by_id(self, location):
        return FakeLocation()

    def ex_get_network_domain(self, location, network_domain):
        return []

    def ex_get_vlan(self, vlan_id):
        return FakeNetwork()

    def ex_list_network_domains(self, location):
        return []

    def ex_list_vlans(self, location):
        return []

    def ex_start_node(self, node):
        return True

    def ex_shutdown_graceful(self, node):
        return True

    def ex_wait_for_state(self, state, func, poll_interval=2, timeout=60, *args, **kwargs):
        return []

    def destroy_node(self, node):
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
        self.plumbery = PlumberyEngine()
        self.plumbery.set_user_name('fake_user')
        self.plumbery.set_user_password('fake_password')
        self.fittings = PlumberyFittings(**fakeFittings)
        self.facility = PlumberyFacility(plumbery=self.plumbery, fittings=self.fittings)
        self.facility.region = FakeRegion()

    def tearDown(self):
        self.facility = None

    def test_build_all_blueprints(self):
        self.facility.build_all_blueprints()

    def test_build_blueprint(self):
        self.facility.build_blueprint('fake')

    def test_destroy_all_nodes(self):
        self.facility.destroy_all_nodes()

    def test_destroy_nodes(self):
        self.facility.destroy_nodes('fake')

    def test_focus(self):
        self.facility.focus()

    def test_get_blueprint(self):
        self.facility.get_blueprint('fake')

    def test_start_all_nodes(self):
        self.facility.start_all_nodes()

    def test_start_nodes(self):
        self.facility.start_nodes('fake')

    def test_stop_all_nodes(self):
        self.facility.stop_all_nodes()

    def test_stop_nodes(self):
        self.facility.stop_nodes('fake')


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
