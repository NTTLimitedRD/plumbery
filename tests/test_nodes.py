#!/usr/bin/env python

"""
Tests for `nodes` module.
"""

import unittest

from plumbery.nodes import PlumberyNodes


class FakeNetwork:

    id = 123


class FakeDomain:

    id = 123
    domain = 'fake'
    network = FakeNetwork()


class FakeImage:

    name = 'RedHat 6 64-bit 4 CPU'


class FakeLocation:

    id = 'EU7'
    name = 'data centre in Amsterdam'
    country = 'Netherlands'


class FakeNode:

    name = 'stackstorm'
    extra = {'datacenterId': 'EU7'}


class FakePlumbery:

    safeMode = False

    def get_shared_secret(self):
        return 'foo'


class FakeRegion:

    def create_node(self, name, image, auth, ex_network_domain, ex_vlan, ex_is_started, ex_description):
        return True

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

    def ex_list_vlans(self, location, network_domain):
        return []

    def ex_wait_for_state(self, state, func, poll_interval=2, timeout=60, *args, **kwargs):
        return []

    def list_nodes(self):
        return []


class FakeFacility:

    plumbery = FakePlumbery()

    region = FakeRegion()

    location = 1

    def get_image(self, name):
        return FakeImage()

    def power_on(self):
        pass

fakeBlueprint = {
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
                }],
          'target': 'fake'
    }


class TestPlumberyNodes(unittest.TestCase):

    def setUp(self):
        self.nodes = PlumberyNodes(FakeFacility())

    def tearDown(self):
        self.nodes = None

    def test_build_blueprint(self):
        domain = FakeDomain()
        self.nodes.build_blueprint(fakeBlueprint, domain)

    def test_destroy_blueprint(self):
        self.nodes.destroy_blueprint(fakeBlueprint)

    def test_get_node(self):
        self.nodes.get_node('stackstorm')

    def test_start_nodes(self):
        self.nodes.start_blueprint('fake')

    def test_stop_nodes(self):
        self.nodes.stop_blueprint('fake')


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
