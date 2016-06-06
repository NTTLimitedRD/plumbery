#!/usr/bin/env python

"""
Tests for `action` module.
"""

import unittest

from plumbery.action import PlumberyAction, PlumberyActionLoader


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

    def test_loader(self):

        action = PlumberyActionLoader.from_shelf('echo', {})
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

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
