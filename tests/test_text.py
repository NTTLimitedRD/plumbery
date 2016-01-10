#!/usr/bin/env python

"""
Tests for `text` module.
"""

import unittest
from mock_api import DimensionDataMockHttp
from libcloud.compute.drivers.dimensiondata import DimensionDataNodeDriver
from plumbery.engine import PlumberyFittings, PlumberyEngine
from plumbery.facility import PlumberyFacility
from plumbery.text import PlumberyText, PlumberyContext, PlumberyNodeContext
from plumbery import __version__


class FakeNode1:

    id = '1234'
    name = 'mongo_mongos01'
    public_ips = ['168.128.12.163']
    private_ips = ['192.168.50.11']
    extra = {'ipv6': '2a00:47c0:111:1136:47c9:5a6a:911d:6c7f',
             'datacenterId': 'EU6'}


class FakeNode2:

    id = '5678'
    name = 'mongo_mongos02'
    public_ips = ['168.128.12.164']
    private_ips = ['192.168.50.12']
    extra = {'ipv6': '2a00:47c0:111:1136:47c9:5a6a:911d:6c7f',
             'datacenterId': 'EU6'}


class FakeRegion:

    def list_nodes(self):
        return [FakeNode1(), FakeNode2()]

    def get_node(self, name):
        return FakeNode2()

class FakeFacility:

    plumbery = PlumberyEngine()
    region = FakeRegion()

    def list_nodes(self):
        return ['mongo_mongos01', 'mongo_mongos02']

    def power_on(self):
        pass

    def get_location_id(self):
        return 'EU6'

class FakeContainer:

    facility = FakeFacility()
    region = FakeRegion()


class TestPlumberyText(unittest.TestCase):

    def setUp(self):
        self.text = PlumberyText()

    def tearDown(self):
        pass

    def test_dictionary(self):

        template = "little {{ test }} with multiple {{test}} and {{}} as well"
        context = PlumberyContext(dictionary={ 'test': 'toast' })
        expected = "little toast with multiple toast and {{}} as well"

        self.assertEqual(
            self.text.expand_variables(template, context), expected)

    def test_engine(self):

        template = "we are running plumbery {{ plumbery.version }}"
        context = PlumberyContext(context=PlumberyEngine())
        expected = "we are running plumbery "+__version__

        self.assertEqual(
            self.text.expand_variables(template, context), expected)

    def test_node1(self):

        template = "{{ mongo_mongos01.public }}"
        context = PlumberyNodeContext(node=FakeNode1())
        expected = '168.128.12.163'
        self.assertEqual(
            self.text.expand_variables(template, context), expected)

        template = "{{mongo_mongos01.private }}"
        expected = '192.168.50.11'
        self.assertEqual(
            self.text.expand_variables(template, context), expected)

        template = "{{ mongo_mongos01}}"
        expected = '192.168.50.11'
        self.assertEqual(
            self.text.expand_variables(template, context), expected)

        template = "{{ mongo_mongos01.ipv6 }}"
        expected = '2a00:47c0:111:1136:47c9:5a6a:911d:6c7f'
        self.assertEqual(
            self.text.expand_variables(template, context), expected)

    def test_node2(self):

        template = "{{ mongo_mongos02.public }}"
        context = PlumberyNodeContext(node=FakeNode1(),
                                      container=FakeContainer())
        expected = '168.128.12.164'
        self.assertEqual(
            self.text.expand_variables(template, context), expected)

        template = "{{ mongo_mongos02.private }}"
        expected = '192.168.50.12'
        self.assertEqual(
            self.text.expand_variables(template, context), expected)

        template = "{{ mongo_mongos02 }}"
        expected = '192.168.50.12'
        self.assertEqual(
            self.text.expand_variables(template, context), expected)

        template = "{{ mongo_mongos02.ipv6 }}"
        expected = '2a00:47c0:111:1136:47c9:5a6a:911d:6c7f'
        self.assertEqual(
            self.text.expand_variables(template, context), expected)


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
