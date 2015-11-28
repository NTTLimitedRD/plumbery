#!/usr/bin/env python

"""
Tests for `polisher` module.
"""

import unittest

from libcloud.compute.types import NodeState

from plumbery.polisher import PlumberyPolisher


class FakeNode(object):
    name = 'fake'
    id = '1234'
    state = NodeState.RUNNING
    private_ips = ['10.100.100.100']
    extra = {'status': {}}

fakeSettings = {
    'name': 'stackstorm',
    'description': 'fake',
    'appliance': 'RedHat 6 64-bit 4 CPU'}


class TestPlumberyPolisher(unittest.TestCase):

    def test_life_cycle(self):
        self.polisher = PlumberyPolisher.from_shelf('spit')

        self.polisher.go()
        self.polisher.shine_node(FakeNode(), fakeSettings)
        self.polisher.reap()


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
