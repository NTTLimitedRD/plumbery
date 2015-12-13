#!/usr/bin/env python

"""
Tests for `polisher` module.
"""

import unittest

from libcloud.compute.types import NodeState

from plumbery.engine import PlumberyFittings
from plumbery.polisher import PlumberyPolisher


class FakeEngine():

    def get_shared_secret(self):
        return 'nuts'


fakeFacilitySettings = {
    'locationId': 'EU6',
    'rub': [{'beachhead': '10.1.10.9'}, {'beachhead': '10.1.10.10'}],
    'regionId': 'dd-eu'}


class FakeFacility():
    fittings = PlumberyFittings(**fakeFacilitySettings)

    def __repr__(self):
        return "<FakeFacility fittings: {}>".format(self.fittings)


class FakeNode():
    name = 'fake'
    id = '1234'
    state = NodeState.RUNNING
    private_ips = ['10.100.100.100']
    public_ips = []
    extra = {'datacenterId': 'EU6',
            'description': '#fake description with #tags',
            'ipv6': '2a00:47c0:111:1208:4802:ab7:cb3c:92ec',
            'status': {}}

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
        self.polisher = PlumberyPolisher.from_shelf('ansible', fakeAnsibleConfiguration)
        self.polisher.go(FakeEngine())
        self.polisher.move_to(FakeFacility())
        self.polisher.shine_node(FakeNode(), fakeNodeSettings)
        self.polisher.reap()

    def test_rub(self):
        self.polisher = PlumberyPolisher.from_shelf('rub', fakeRubConfiguration)
        self.polisher.go(FakeEngine())
        self.polisher.move_to(FakeFacility())
        self.polisher.shine_node(FakeNode(), fakeNodeSettings)
        self.polisher.reap()

    def test_inventory(self):
        self.polisher = PlumberyPolisher.from_shelf('inventory', fakeInventoryConfiguration)
        self.polisher.go(FakeEngine())
        self.polisher.move_to(FakeFacility())
        self.polisher.shine_node(FakeNode(), fakeNodeSettings)
        self.polisher.reap()

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
