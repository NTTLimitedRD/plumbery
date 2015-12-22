#!/usr/bin/env python

"""
Tests for `domain` module.
"""

import unittest

from plumbery.domain import PlumberyDomain
from mock_api import DimensionDataMockHttp
from libcloud.compute.drivers.dimensiondata import DimensionDataNodeDriver

DIMENSIONDATA_PARAMS = ('user', 'password')


class FakeDomain:

    id = 123


class FakeNetwork:

    id = 123


class FakePlumbery:

    safeMode = False


class FakeFacility:

    plumbery = FakePlumbery()

    DimensionDataNodeDriver.connectionCls.conn_classes = (None, DimensionDataMockHttp)
    DimensionDataMockHttp.type = None
    region = DimensionDataNodeDriver(*DIMENSIONDATA_PARAMS)

    location = 1


fakeBluePrint = {'domain': {'name': 'fake',
                            'service': 'ADVANCED',
                            'description': '#vdc1'},
                'ethernet': {'name': 'fake',
                            'subnet': '10.0.10.0',
                            'description': '#vdc1'}}


class TestPlumberyDomain(unittest.TestCase):

    def setUp(self):
        facility = FakeFacility()
        self.domain = PlumberyDomain(facility=facility)

    def tearDown(self):
        self.domain = None

    def test_000(self):
        self.domain.build(fakeBluePrint)


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
