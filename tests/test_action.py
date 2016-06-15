#!/usr/bin/env python

"""
Tests for `action` module.
"""

import unittest

from plumbery.action import PlumberyAction, PlumberyActionLoader
from plumbery.util import PlumberyParameters


class TestPlumberyAction(unittest.TestCase):

    def test_signatures(self):

        class DummyAction(PlumberyAction):
            def __init__(self, settings):
                self.count = 0

            def ignite(self, engine):
                self.count += 100

            def enter(self, facility):
                self.count *= 2

            def handle(self, blueprint):
                self.count += 1

            def quit(self):
                self.count += 3

            def reap(self):
                self.count += 1

        action = DummyAction({})
        action.ignite(engine=None)
        action.enter(facility=None)
        action.handle(blueprint=None)
        action.handle(blueprint=None)
        action.quit()
        action.enter(facility=None)
        action.handle(blueprint=None)
        action.handle(blueprint=None)
        action.quit()
        action.enter(facility=None)
        action.handle(blueprint=None)
        action.handle(blueprint=None)
        action.quit()
        action.reap()
        self.assertEqual(action.count, 836)

    def test_loader_ok(self):

        action = PlumberyActionLoader.from_shelf('dummy')
        action.ignite(engine=None)
        action.enter(facility=None)
        action.handle(blueprint=None)
        action.handle(blueprint=None)
        action.quit()
        action.enter(facility=None)
        action.handle(blueprint=None)
        action.handle(blueprint=None)
        action.quit()
        action.enter(facility=None)
        action.handle(blueprint=None)
        action.handle(blueprint=None)
        action.quit()
        action.reap()

    def test_loader_unknown_class(self):

        with self.assertRaises(ImportError):
            action = PlumberyActionLoader.from_shelf('*123*')

    def test_getters(self):
        action = PlumberyActionLoader.from_shelf('dummy', {'dummy': 'ok'})
        self.assertEqual(action.get_type(), 'dummy')
        self.assertEqual(action.get_parameter('dummy'), 'ok')

        parameters = PlumberyParameters({'goofy': 'ok'})
        action = PlumberyActionLoader.from_shelf('dummy', parameters)
        self.assertEqual(action.get_type(), 'dummy')
        self.assertEqual(action.get_parameter('goofy'), 'ok')

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
