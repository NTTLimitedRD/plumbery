#!/usr/bin/env python

"""
Tests for `plumbery` module.
"""

import os
import sys
import unittest

from plumbery.engine import PlumberyEngine

os.environ['SHARED_SECRET'] = "WhatsUpDoc"


class TestPlumberyEngine(unittest.TestCase):

    def setUp(self):
        self.engine = PlumberyEngine()

    def tearDown(self):
        self.engine = None

    def test_setters_and_getters(self):

        self.engine.set_shared_secret('fake_secret')
        self.assertEqual(self.engine.get_shared_secret(), 'fake_secret')

        self.engine.set_user_name('fake_name')
        self.assertEqual(self.engine.get_user_name(), 'fake_name')

        self.engine.set_user_password('fake_password')
        self.assertEqual(self.engine.get_user_password(), 'fake_password')


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
