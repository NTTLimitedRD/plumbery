#!/usr/bin/env python

"""
Tests for `infrastructure` module.
"""

import unittest

from libcloud.compute.drivers.dimensiondata import DimensionDataNodeDriver
from mock_api import DimensionDataMockHttp

from plumbery.infrastructure import PlumberyInfrastructure

DIMENSIONDATA_PARAMS = ('user', 'password')


class FakeDomain:

    id = 123


class FakeNetwork:

    id = 123


class FakePlumbery:

    safeMode = False

class FakeLocation:

    id = 'EU6'

class FakeFacility:

    plumbery = FakePlumbery()

    DimensionDataNodeDriver.connectionCls.conn_classes = (None, DimensionDataMockHttp)
    DimensionDataMockHttp.type = None
    region = DimensionDataNodeDriver(*DIMENSIONDATA_PARAMS)

    location = FakeLocation()

    _cache_network_domains = []
    _cache_vlans = []

fakeBluePrint = {'domain': {'name': 'fake',
                            'service': 'ADVANCED',
                            'description': '#vdc1'},
                'ethernet': {'name': 'fake',
                            'subnet': '10.0.10.0',
                            'description': '#vdc1'}}


class TestPlumberyInfrastructure(unittest.TestCase):

    def setUp(self):
        facility = FakeFacility()
        self.infrastructure = PlumberyInfrastructure(facility=facility)

    def tearDown(self):
        self.infrastructure = None

    def test_build(self):
        self.infrastructure.build(fakeBluePrint)

    def test_get_container(self):
        container = self.infrastructure.get_container(fakeBluePrint)
        self.assertEqual(container.domain, None)
        self.assertEqual(container.network, None)

    def test_get_ethernet(self):
        self.infrastructure.get_ethernet('MyNetwork')
#        self.infrastructure.get_ethernet(['XY6', 'MyNetwork'])
#        self.infrastructure.get_ethernet(['dd-eu', 'EU6', 'MyNetwork'])

    def test_get_ipv4(self):
        self.infrastructure.blueprint = fakeBluePrint
        self.infrastructure._get_ipv4()

    def test_get_network_domain(self):
        self.infrastructure.blueprint = fakeBluePrint
        self.infrastructure.get_network_domain('fake')

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
