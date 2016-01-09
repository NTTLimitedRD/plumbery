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

# should be removed - head


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

    def create_node(self, name, image, auth, ex_network_domain, ex_vlan,
                    ex_is_started, ex_description):
        return True

    def ex_create_network_domain(self, location, name, service_plan,
                                 description):
        return FakeDomain()

    def ex_create_vlan(self, network_domain, name, private_ipv4_base_address,
                       description):
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

    def ex_wait_for_state(self, state, func, poll_interval=2, timeout=60,
                          *args, **kwargs):
        return []

    def destroy_node(self, node):
        return True

    def list_images(self, location):
        return [FakeImage()]

    def list_nodes(self):
        return [FakeNode()]


# should be removed - end

fakeFittings = {
    'regionId': 'dd-na',
    'locationId': 'NA9',
    'basement': 'fake unknown',
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
        },{
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
        },{
        'macro': 'unknown fake'
        }]
    }


class TestPlumberyFacility(unittest.TestCase):

    def setUp(self):
        self.plumbery = PlumberyEngine()
        self.plumbery.set_user_name('fake_user')
        self.plumbery.set_user_password('fake_password')
        self.fittings = PlumberyFittings(**fakeFittings)
        DimensionDataNodeDriver.connectionCls.conn_classes = (
            None, DimensionDataMockHttp)
        DimensionDataMockHttp.type = None
        self.facility = PlumberyFacility(
            plumbery=self.plumbery, fittings=self.fittings)
        self.facility.region = DimensionDataNodeDriver(*DIMENSIONDATA_PARAMS)

    def tearDown(self):
        self.facility = None

    def test_get_location_id(self):
        self.assertEqual(self.facility.get_location_id(), 'NA9')

    def test_list_basement(self):
        self.assertEqual(self.facility.list_basement(), ['fake'])

    def test_list_blueprints(self):
        self.assertEqual(self.facility.list_blueprints(), ['fake'])

    def test_expand_blueprint(self):
        self.assertEqual(
            self.facility.expand_blueprint('fake'), ['fake'])
        self.assertEqual(
            self.facility.expand_blueprint('fake unknown fake'), ['fake'])
        self.assertEqual(
            self.facility.expand_blueprint('macro'), ['fake'])
        self.assertEqual(
            self.facility.expand_blueprint('basement'), ['fake'])

    def test_get_blueprint(self):
        self.assertEqual(
            self.facility.get_blueprint('fake')['target'], 'fake')
        self.assertIsNone(self.facility.get_blueprint('macro'))
        self.assertIsNone(self.facility.get_blueprint('crazyAndunknown'))

    def test_list_domains(self):
        self.assertEqual(self.facility.list_domains(), ['VDC1'])

    def test_list_ethernets(self):
        self.assertEqual(self.facility.list_ethernets(), ['vlan1'])

    def test_list_nodes(self):
        self.assertEqual(self.facility.list_nodes(), ['stackstorm'])

    def test_get_image(self):
        self.assertRegexpMatches(
            self.facility.get_image().name, "^RedHat ")
        self.assertIsNone(self.facility.get_image('perfectlyUnknown'))

    def test_focus(self):
        self.facility.focus()

    def test_build_all_blueprints(self):
        self.facility.build_all_blueprints()

    def test_build_blueprint(self):
        self.facility.build_blueprint('fake')

    def test_destroy_all_nodes(self):
        self.facility.destroy_all_nodes()

    def test_destroy_nodes(self):
        self.facility.destroy_nodes('fake')

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
