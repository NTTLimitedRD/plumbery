"""
Tests for `facility` module.
"""

# special construct to allow relative import
#
if __name__ == "__main__" and __package__ is None:
    __package__ = "tests"
from tests import dummy

import unittest

from libcloud.compute.drivers.dimensiondata import DimensionDataNodeDriver

from plumbery.action import PlumberyAction
from plumbery.engine import PlumberyEngine
from plumbery.facility import PlumberyFacility

from .mock_api import DimensionDataMockHttp
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
    'basement': 'fake1 unknown',
    'blueprints': [{
        'fake1': {
            'domain': {
                'name': 'VDC1',
                'service': 'ADVANCED',
                'description': 'fake'},
            'ethernet': {
                'name': 'vlan1',
                'subnet': '10.0.10.0',
                'description': 'fake'},
            'nodes': [{
                'stackstorm1': {
                    'description': 'fake',
                    'appliance': 'RedHat 6 64-bit 4 CPU'
                    }
                }]
            }
        }, {
        'fake2': {
            'domain': {
                'name': 'VDC1',
                'service': 'ADVANCED',
                'description': 'fake'},
            'ethernet': {
                'name': 'vlan1',
                'subnet': '10.0.10.0',
                'description': 'fake'},
            'nodes': [{
                'stackstorm2': {
                    'description': 'fake',
                    'appliance': 'RedHat 6 64-bit 4 CPU'
                    }
                }]
            }
        }, {
        'macro': 'unknown fake2'
        }]
    }

defaultsPlan = """
---
safeMode: True

defaults:
  locationId: EU6
  regionId: dd-eu
  domain:
    name: fake
    ipv4: auto
  ethernet:
    name: myVLAN
    subnet: 10.1.10.0
  bee:
    information:
      - one line of information
    cpu: 3
    memory: 6
    cloud-config:
      disable_root: true
      packages:
        - ntp
      runcmd:
        - echo "hello"
  cloud-config:
    disable_root: false
    ssh_pwauth: true
    packages:
      - foo
      - bar
    runcmd:
      - echo "romeo"
      - echo "juliet"
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
        accept:
          - NA19::remoteNetwork
      nodes:
        - myServer:
            default: bee
            information:
              - complementary information
            memory: 5
            cloud-config:
              packages:
                - smtp
              runcmd:
                - echo "world"
"""


class FakeAction(PlumberyAction):
    def __init__(self, settings):
        self.count = 3

    def ignite(self, engine):
        self.count += 100

    def enter(self, facility):
        self.count *= 2

    def handle(self, blueprint):
        self.count += 5

    def quit(self):
        self.count -= 2

    def reap(self):
        self.count += 1

class TestPlumberyFacility(unittest.TestCase):

    def setUp(self):
        self.plumbery = PlumberyEngine()
        self.plumbery.set_user_name('fake_user')
        self.plumbery.set_user_password('fake_password')
        DimensionDataNodeDriver.connectionCls.conn_classes = (
            None, DimensionDataMockHttp)
        DimensionDataMockHttp.type = None
        self.plumbery.region = DimensionDataNodeDriver(*DIMENSIONDATA_PARAMS)
        self.facility = PlumberyFacility(
            plumbery=self.plumbery, fittings=fakeFittings)
        self.facility.power_on()

    def tearDown(self):
        self.facility = None

    def test_get_location_id(self):
        self.assertEqual(self.facility.get_location_id(), 'NA9')

    def test_list_basement(self):
        self.assertEqual(self.facility.list_basement(), ['fake1'])

    def test_list_blueprints(self):
        self.assertEqual(self.facility.list_blueprints(), ['fake1', 'fake2'])

    def test_expand_blueprint(self):
        self.assertEqual(
            self.facility.expand_blueprint('fake1'), ['fake1'])
        self.assertEqual(
            self.facility.expand_blueprint('fake1 unknown fake'), ['fake1'])
        self.assertEqual(
            self.facility.expand_blueprint('macro'), ['fake2'])
        self.assertEqual(
            self.facility.expand_blueprint('basement'), ['fake1'])

    def test_get_blueprint(self):
        self.assertEqual(
            self.facility.get_blueprint('fake2')['target'], 'fake2')
        self.assertIsNone(self.facility.get_blueprint('macro'))
        self.assertIsNone(self.facility.get_blueprint('crazyAndunknown'))

    def test_list_domains(self):
        self.assertEqual(self.facility.list_domains(), ['VDC1'])

    def test_list_ethernets(self):
        self.assertEqual(self.facility.list_ethernets(), ['vlan1'])

    def test_list_nodes(self):
        self.assertEqual(self.facility.list_nodes(),
                         ['stackstorm1', 'stackstorm2'])

    def test_get_image(self):
        self.assertRegexpMatches(
            self.facility.get_image().name, "^RedHat ")
        self.assertIsNone(self.facility.get_image('perfectlyUnknown'))

    def test_focus(self):
        self.facility.focus()

    def test_process_all_blueprints(self):
        action = FakeAction({})
        self.facility.process_all_blueprints(action)
        self.assertEqual(action.count, 14)

    def test_process_blueprint(self):
        action = FakeAction({})
        self.facility.process_blueprint(action, names='fake')
        self.assertEqual(action.count, 4)

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
        self.assertEqual(self.facility.lookup('location.country'), 'US')
        self.assertEqual(self.facility.lookup('location.id'), 'NA9')
        self.assertEqual(self.facility.lookup('*unknown*'), None)

    def test_settings(self):
        engine = PlumberyEngine(defaultsPlan)
        facility = engine.list_facility('EU6')[0]
        self.assertEqual(facility.get_setting('locationId'), 'EU6')
        self.assertEqual(facility.get_setting('regionId'), 'dd-eu')
        self.assertEqual(facility.get_setting('prepare'), None)
        self.assertEqual(facility.get_setting('basement'), 'myBlueprint')

    def test_settings_private(self):
        settings = {
            'apiHost': 'smee.com',
            'locationId': 'NA5',
            'safeMode': True
        }
        engine = PlumberyEngine(plan=settings)
        engine.set_user_name('smee')
        engine.set_user_password('smee')
        facility = engine.list_facility()[0]
#        facility.power_on()
        self.assertEqual(facility.get_setting('locationId'), 'NA5')
        self.assertIsNone(facility.get_setting('regionId'))

    def test_blueprints(self):
        engine = PlumberyEngine(defaultsPlan)
        facility = engine.list_facility('EU6')[0]
        blueprint = facility.get_blueprint('myBlueprint')
        self.assertEqual(isinstance(blueprint, dict), True)
        self.assertEqual(blueprint['domain']['name'], 'myDC')
        self.assertEqual(blueprint['domain']['ipv4'], 'auto')
        self.assertEqual(blueprint['ethernet']['name'], 'myVLAN')
        self.assertEqual(blueprint['ethernet']['subnet'], '10.1.10.0')
        self.assertEqual(len(blueprint['ethernet']['accept']), 1)
        label = list(blueprint['nodes'][0])[0]
        node = blueprint['nodes'][0][label]
        self.assertEqual('default' not in node, True)
        self.assertEqual(node['cpu'], 3)
        self.assertEqual(node['memory'], 5)
        self.assertEqual(len(node['information']), 2)
        config = node['cloud-config']
        self.assertEqual(isinstance(config, dict), True)
        self.assertEqual(config['disable_root'], True)
        self.assertEqual(config['ssh_pwauth'], True)
        self.assertEqual(len(config['packages']), 4)
        self.assertEqual(len(config['runcmd']), 4)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
