#!/usr/bin/env python

"""
Tests for `polisher` module.
"""

import unittest

from libcloud.compute.types import NodeState

from plumbery.engine import PlumberyFittings
from plumbery.polisher import PlumberyPolisher


class FakeNetwork:

    id = 123


class FakeEngine():

    def get_shared_secret(self):
        return 'nuts'


class FakeRegion:

    def create_node(self, name, image, auth, ex_network_domain, ex_vlan,
                    ex_is_started, ex_description):
        return True

    def ex_create_vlan(self, network_domain, name, private_ipv4_base_address,
                       description):
        return FakeNetwork()

    def ex_get_network_domain(self, location, network_domain):
        return []

    def ex_get_vlan(self, vlan_id):
        return FakeNetwork()

    def ex_list_nat_rules(self, domain):
        return []

    def ex_list_network_domains(self, location):
        return []

    def ex_list_vlans(self, location):
        return []

    def ex_start_node(self, node):
        return True

    def ex_shutdown_graceful(self, node):
        return True

    def ex_wait_for_state(self, state, func, poll_interval=2, timeout=60,
                          *args, **kwargs):
        return []

    def destroy_node(self, node):
        return True

    def list_nodes(self):
        return [FakeNode()]


class FakeContainer:

    id = 123
    domain = 'fake'
    network = FakeNetwork()

    region = FakeRegion()

    blueprint = {
        'target': 'fake',
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

    def get_network_domain(self, blueprint):
        return None

    def get_ethernet(self, blueprint):
        return None

    def _add_to_pool(self, node):
        pass

fakeFacilitySettings = {
    'locationId': 'EU6',
    'rub': [{'beachhead': '10.1.10.9'}, {'beachhead': '10.1.10.10'}],
    'regionId': 'dd-eu'}


class FakeFacility():
    plumbery = FakeEngine()
    fittings = PlumberyFittings(**fakeFacilitySettings)
    region = FakeRegion()

    def __repr__(self):
        return "<FakeFacility fittings: {}>".format(self.fittings)


class FakeNode():
    name = 'fake'
    id = '1234'
    state = NodeState.RUNNING
    private_ips = ['12.34.56.78']
    public_ips = []
    extra = {'datacenterId': 'EU6',
             'description': '#fake description with #tags',
             'ipv6': 'fe80::'}

fakeNodeSettings = {
    'name': 'stackstorm',
    'description': 'fake',
    'appliance': 'RedHat 6 64-bit 4 CPU',
    'rub': ['rub.update.sh', 'rub.docker.sh']}

fakeAnsibleConfiguration = {
    'reap': 'test_polisher_ansible.yaml'}

fakeRubConfiguration = {
    'reap': 'test_polisher_rub.yaml',
    'key': 'test_polisher.pub'}

fakeInventoryConfiguration = {
    'reap': 'test_polisher_inventory.yaml'}


class TestPlumberyPolisher(unittest.TestCase):

    def test_ansible(self):
        self.polisher = PlumberyPolisher.from_shelf(
            'ansible', fakeAnsibleConfiguration)
        self.polisher.go(FakeEngine())
        self.polisher.move_to(FakeFacility())
        self.polisher.shine_node(FakeNode(), fakeNodeSettings, FakeContainer())
        self.polisher.reap()

    def test_inventory(self):
        self.polisher = PlumberyPolisher.from_shelf(
            'inventory', fakeInventoryConfiguration)
        self.polisher.go(FakeEngine())
        self.polisher.move_to(FakeFacility())
        self.polisher.shine_node(
            FakeNode(), fakeNodeSettings, FakeContainer())
        self.polisher.reap()

    def test_rub(self):
        self.polisher = PlumberyPolisher.from_shelf(
            'rub', fakeRubConfiguration)
        self.polisher.go(FakeEngine())
        self.polisher.move_to(FakeFacility())
        self.polisher.shine_node(FakeNode(), fakeNodeSettings, FakeContainer())
        self.polisher.reap()

    def test_spit(self):
        self.polisher = PlumberyPolisher.from_shelf(
            'spit', fakeInventoryConfiguration)
        self.polisher.go(FakeEngine())
        self.polisher.move_to(FakeFacility())
        self.polisher.shine_node(
            FakeNode(), fakeNodeSettings, FakeContainer())
        self.polisher.reap()

    def test_ping(self):
        self.polisher = PlumberyPolisher.from_shelf(
            'ping', fakeInventoryConfiguration)
        self.polisher.go(FakeEngine())
        self.polisher.move_to(FakeFacility())
        self.polisher.shine_node(
            FakeNode(), fakeNodeSettings, FakeContainer())
        self.polisher.reap()

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
