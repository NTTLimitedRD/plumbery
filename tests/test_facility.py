#!/usr/bin/env python

"""
Tests for `facility` module.
"""

import unittest
from mock_api import DimensionDataMockHttp
from libcloud.compute.drivers.dimensiondata import DimensionDataNodeDriver
from plumbery.engine import PlumberyFittings, PlumberyEngine
from plumbery.facility import PlumberyFacility

DIMENSIONDATA_PARAMS = ('user', 'password')


class FakeElement:

    def find(self, dummy):
        return {'ipv6': 'nuts'}

fakeFittings = {
    'regionId': 'dd-na',
    'locationId': 'NA9',
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
        DimensionDataNodeDriver.connectionCls.conn_classes = (None, DimensionDataMockHttp)
        DimensionDataMockHttp.type = None
        self.facility = PlumberyFacility(plumbery=self.plumbery, fittings=self.fittings)
        self.facility.region = DimensionDataNodeDriver(*DIMENSIONDATA_PARAMS)

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
