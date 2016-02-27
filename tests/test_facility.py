#!/usr/bin/env python

"""
Tests for `facility` module.
"""

import unittest

from mock_api import DimensionDataMockHttp
from libcloud.compute.drivers.dimensiondata import DimensionDataNodeDriver

from plumbery.engine import PlumberyEngine
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

defaultsPlan = """
---
safeMode: True
defaults:
  locationId: EU6
  regionId: dd-eu
  ipv4: auto
cloud-config:
  disable_root: false
  ssh_pwauth: true
  ssh_keys:
    rsa_private: |
      {{ pair1.rsa_private }}

    rsa_public: "{{ pair1.ssh.rsa_public }}"

---

basement: myBlueprint

blueprints:

  - myBlueprint:
      domain:
        name: myDC
      ethernet:
        name: myVLAN
        subnet: 10.1.10.0
      nodes:
        - myServer
"""

class TestPlumberyFacility(unittest.TestCase):

    def setUp(self):
        self.plumbery = PlumberyEngine()
        self.plumbery.set_user_name('fake_user')
        self.plumbery.set_user_password('fake_password')
        DimensionDataNodeDriver.connectionCls.conn_classes = (
            None, DimensionDataMockHttp)
        DimensionDataMockHttp.type = None
        self.facility = PlumberyFacility(
            plumbery=self.plumbery, fittings=fakeFittings)
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

    def test_start_all_blueprints(self):
        self.facility.start_all_blueprints()

    def test_start_blueprint(self):
        self.facility.start_blueprint('fake')

    def test_polish_all_blueprints(self):
        self.facility.polish_all_blueprints(polishers='ping')

    def test_polish_blueprint(self):
        self.facility.polish_blueprint(names='fake', polishers='ping')

    def test_stop_all_blueprints(self):
        self.facility.stop_all_blueprints()

    def test_stop_blueprint(self):
        self.facility.stop_blueprint('fake')

    def test_wipe_all_blueprints(self):
        self.facility.wipe_all_blueprints()

    def test_wipe_blueprint(self):
        self.facility.wipe_blueprint('fake')

    def test_destroy_all_blueprints(self):
        self.facility.destroy_all_blueprints()

    def test_destroy_blueprint(self):
        self.facility.destroy_blueprint('fake')

    def test_lookup(self):
        self.assertEqual(self.facility.lookup('location.city'), 'Ashburn')
        self.assertEqual(self.facility.lookup('location.coordinates'),
                         [39.04372, -77.48749])
        self.assertEqual(self.facility.lookup('*unknown*'), None)

    def test_get_parameter(self):

        engine = PlumberyEngine()
        engine.from_text(defaultsPlan)
        facility = engine.list_facility('EU6')[0]
        self.assertEqual(facility.get_parameter('locationId'), 'EU6')
        self.assertEqual(facility.get_parameter('regionId'), 'dd-eu')
        self.assertEqual(facility.get_parameter('rub'), None)
        self.assertEqual(facility.get_parameter('ipv4'), 'auto')
        self.assertEqual(facility.get_parameter('basement'), 'myBlueprint')

        city = facility.get_city()
        self.assertEqual(city, 'Frankfurt')
        self.assertEqual(city, facility.get_city('EU6'))

        coordinates = facility.get_coordinates()
        self.assertEqual(len(coordinates), 2)
        self.assertEqual(coordinates, facility.get_coordinates('EU6'))

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
