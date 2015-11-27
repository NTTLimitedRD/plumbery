#!/usr/bin/env python

"""
Tests for `polisher` module.
"""

import sys
import unittest

from libcloud.compute.types import NodeState

from plumbery.polisher import PlumberyPolisher
from plumbery.exceptions import PlumberyException


class TestPlumberyPolisher(unittest.TestCase):

    def setUp(self):
        self.polisher = PlumberyPolisher.from_shelf('spit')

    def tearDown(self):
        self.polisher = None

    def testPolish(self):

        class FakeNode(object):
            name = 'fake'
            state = NodeState.RUNNING
            private_ips = ['10.100.100.100']

        try:
            self.polisher.shine_node(FakeNode())
        except PlumberyException:
            pass


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
