#!/usr/bin/env python

"""
Tests for `polisher` module.
"""

import os
import unittest

from libcloud.compute.types import NodeState

from plumbery.polisher import PlumberyPolisher


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

        os.environ["SHARED_SECRET"] = "WhatsUpDoc"

        self.polisher.shine_node(FakeNode())


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
