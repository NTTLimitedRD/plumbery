#!/usr/bin/env python

"""
Tests for `nodes` module.
"""

import unittest

from plumbery.nodes import PlumberyNodes
from mock_api import DimensionDataMockHttp
from libcloud.compute.drivers.dimensiondata import DimensionDataNodeDriver

DIMENSIONDATA_PARAMS = ('user', 'password')


class FakeNetwork:

    id = 123


class FakeDomain:

    id = 123
    domain = 'fake'
    network = FakeNetwork()


class FakeImage:

    name = 'RedHat 6 64-bit 4 CPU'


class FakePlumbery:

    safeMode = False

    def get_shared_secret(self):
        return 'foo'


class FakeFacility:

    plumbery = FakePlumbery()
    DimensionDataNodeDriver.connectionCls.conn_classes = (None, DimensionDataMockHttp)
    DimensionDataMockHttp.type = None
    region = DimensionDataNodeDriver(*DIMENSIONDATA_PARAMS)

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
