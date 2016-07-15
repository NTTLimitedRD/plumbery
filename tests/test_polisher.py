#!/usr/bin/env python

"""
Tests for `polisher` module.
"""

# special construct to allow relative import
#
if __name__ == "__main__" and __package__ is None:
    __package__ = "tests"
from tests import dummy

from collections import namedtuple
import unittest

from libcloud.compute.drivers.dimensiondata import DimensionDataNodeDriver
from libcloud.compute.types import NodeState

from plumbery.engine import PlumberyEngine
from plumbery.infrastructure import PlumberyInfrastructure
from plumbery.nodes import PlumberyNodes
from plumbery.polisher import PlumberyPolisher

from .mock_api import DimensionDataMockHttp
DIMENSIONDATA_PARAMS = ('user', 'password')


class FakeNetwork:

    id = 123


class FakeEngine():

    information = []

    def get_shared_secret(self):
        return 'nuts'

    def get_default(self, label, default=None):
        return default


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


fakeFacilitySettings = {
    'locationId': 'EU6',
    'prepare': [{'beachhead': '10.1.10.9'}, {'beachhead': '10.1.10.10'}],
    'regionId': 'dd-eu'}


class FakeFacility():
    plumbery = FakeEngine()
    settings = fakeFacilitySettings
    region = FakeRegion()
    backup = None

    def __repr__(self):
        return "<FakeFacility fittings: {}>".format(self.fittings)

    def get_location_id(self):
        return 'EU6'

    def get_setting(self, label, default=None):
        if label in self.settings:
            return self.settings[label]

        return default

    def power_on(self):
        pass


class FakeContainer:

    id = 123
    domain = 'fake'
    network = FakeNetwork()

    region = FakeRegion()
    facility = FakeFacility()

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

FakeStatus = namedtuple('FakeStatus', 'action')


class FakeNode():

    def __init__(self):
        self.name = 'fake'
        self.id = '1234'
        self.state = NodeState.RUNNING
        self.private_ips = ['12.34.56.78']
        self.public_ips = []
        self.extra = {'datacenterId': 'EU6',
                      'description': '#fake description with #tags',
                      'ipv6': 'fe80::', 'here': 'there',
                      'status': FakeStatus('none'),
                      'dummy': 'test'}

fakeNodeSettings = {
    'name': 'stackstorm',
    'description': 'fake',
    'appliance': 'RedHat 6 64-bit 4 CPU',
    'information': ['hello world'],
    'prepare': ['prepare.update.sh', 'prepare.docker.sh']}

fakePrepareConfiguration = {
    'key': 'test_polisher.pub'}


myInformation = """
---
information:
  - plan-level information
---
locationId: NA9
regionId: dd-na
information:
  - facility-level information

blueprints:

  - test:
      domain:
        description: fake
        name: myDC
      ethernet:
        description: fake
        name: myVLAN
        subnet: 10.1.10.0
      information:
        - container-level information
      nodes:
        - stackstorm:
            description: fake
            appliance: 'RedHat 6 64-bit 4 CPU'
            cpu: 2
            memory: 2
            disks:
              - 1 10 highperformance
            glue:
              - internet 22
            monitoring: essentials
            information:
              - hello world
            prepare:
              - prepare.update.sh
              - prepare.docker.sh
        - node1:
            information:
              - node-level information
"""


def do_polish(polisher):

    engine = PlumberyEngine(myInformation)
    engine.set_shared_secret('fake_secret')
    engine.set_user_name('fake_name')
    engine.set_user_password('fake_password')

    polisher.go(engine)

    facility = engine.list_facility('NA9')[0]
    DimensionDataNodeDriver.connectionCls.conn_classes = (
        None, DimensionDataMockHttp)
    DimensionDataMockHttp.type = None
    facility.region = DimensionDataNodeDriver(*DIMENSIONDATA_PARAMS)

    polisher.move_to(facility)

    blueprint = facility.get_blueprint('test')
    infrastructure = PlumberyInfrastructure(facility)
    container = infrastructure.get_container(blueprint)

    polisher.shine_container(container)

    nodes = PlumberyNodes(facility)

    node = nodes.get_node('stackstorm')
    polisher.shine_node(
        node=node, settings=fakeNodeSettings, container=container)

    node = nodes.get_node('node1')
    polisher.shine_node(
        node=node, settings=fakeNodeSettings, container=container)

    polisher.move_to(FakeFacility())

    polisher.shine_container(FakeContainer())

    polisher.shine_node(
        node=FakeNode(), settings=fakeNodeSettings, container=FakeContainer())

    polisher.reap()


class TestPlumberyPolisher(unittest.TestCase):

    def test_ansible(self):
        polisher = PlumberyPolisher.from_shelf('ansible', {})
        do_polish(polisher)

    def test_configure(self):
        polisher = PlumberyPolisher.from_shelf('configure', {})
        do_polish(polisher)

    def test_information(self):
        polisher = PlumberyPolisher.from_shelf('information', {})
        do_polish(polisher)

    def test_inventory(self):
        polisher = PlumberyPolisher.from_shelf('inventory', {})
        do_polish(polisher)

    def test_ping(self):
        polisher = PlumberyPolisher.from_shelf('ping', {})
        do_polish(polisher)

    def test_prepare(self):
        polisher = PlumberyPolisher.from_shelf(
            'prepare', fakePrepareConfiguration)
        do_polish(polisher)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
