#!/usr/bin/env python

"""
Tests for `polisher` module.
"""

from collections import namedtuple
import logging
import unittest

from mock_api import DimensionDataMockHttp
from libcloud.compute.drivers.dimensiondata import DimensionDataNodeDriver

from libcloud.compute.types import NodeState

from plumbery.engine import PlumberyEngine
from plumbery.facility import PlumberyFacility
from plumbery.infrastructure import PlumberyInfrastructure
from plumbery.nodes import PlumberyNodes
from plumbery.polisher import PlumberyPolisher

DIMENSIONDATA_PARAMS = ('user', 'password')


class FakeNetwork:

    id = 123


class FakeEngine():

    information = []

    def get_shared_secret(self):
        return 'nuts'

    def get_cloud_config(self):
        return {}

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
    parameters = fakeFacilitySettings
    region = FakeRegion()

    def __repr__(self):
        return "<FakeFacility fittings: {}>".format(self.fittings)

    def get_parameter(self, label, default=None):
        if label in self.parameters:
            return self.parameters[label]

        return default


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
    'rub': ['rub.update.sh', 'rub.docker.sh']}

fakeRubConfiguration = {
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
        name: myDC
      ethernet:
        name: myVLAN
        subnet: 10.1.10.0
      information:
        - container-level information
      nodes:
        node1:
          - node-level information
"""

class TestPlumberyPolisher(unittest.TestCase):


    def test_information(self):
        polisher = PlumberyPolisher.from_shelf('information', {})
        polisher.go(FakeEngine())
        polisher.move_to(FakeFacility())
        polisher.shine_node(
            FakeNode(), fakeNodeSettings, FakeContainer())
        polisher.reap()

    def test_information_textual(self):
        engine = PlumberyEngine()
        engine.from_text(myInformation)
        polisher = PlumberyPolisher.from_shelf('information', {})
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
        node = nodes.get_node('node1')
        polisher.shine_node(
            node=node, settings=fakeNodeSettings, container=container)
        polisher.reap()

    def test_ping(self):
        polisher = PlumberyPolisher.from_shelf('ping', {})
        polisher.go(FakeEngine())
        polisher.move_to(FakeFacility())
        polisher.shine_node(
            FakeNode(), fakeNodeSettings, FakeContainer())
        polisher.reap()

    def test_ansible(self):
        polisher = PlumberyPolisher.from_shelf('ansible', {})
        polisher.go(FakeEngine())
        polisher.move_to(FakeFacility())
        polisher.shine_node(FakeNode(), fakeNodeSettings, FakeContainer())
        polisher.reap()

    def test_inventory(self):
        polisher = PlumberyPolisher.from_shelf('inventory', {})
        polisher.go(FakeEngine())
        polisher.move_to(FakeFacility())
        polisher.shine_node(
            FakeNode(), fakeNodeSettings, FakeContainer())
        polisher.reap()

    def test_rub(self):
        polisher = PlumberyPolisher.from_shelf(
            'rub', fakeRubConfiguration)
        polisher.go(FakeEngine())
        polisher.move_to(FakeFacility())
        polisher.shine_node(FakeNode(), fakeNodeSettings, FakeContainer())
        polisher.reap()

    def test_spit(self):
        polisher = PlumberyPolisher.from_shelf('spit', {})
        polisher.go(FakeEngine())
        polisher.move_to(FakeFacility())
        polisher.shine_node(
            FakeNode(), fakeNodeSettings, FakeContainer())
        polisher.reap()

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
