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

            def begin(self, engine):
                self.count += 100

            def enter(self, facility):
                self.count *= 2

            def process(self, blueprint):
                self.count += 1

            def quit(self):
                self.count += 3

            def end(self):
                self.count += 1

        action = DummyAction({})
        action.begin(engine=None)
        action.enter(facility=None)
        action.process(blueprint=None)
        action.process(blueprint=None)
        action.quit()
        action.enter(facility=None)
        action.process(blueprint=None)
        action.process(blueprint=None)
        action.quit()
        action.enter(facility=None)
        action.process(blueprint=None)
        action.process(blueprint=None)
        action.quit()
        action.end()
        self.assertEqual(action.count, 836)

    def test_loader_ok(self):

        action = PlumberyActionLoader.load('noop')
        action.begin(engine=None)
        action.enter(facility=None)
        action.process(blueprint=None)
        action.process(blueprint=None)
        action.quit()
        action.enter(facility=None)
        action.process(blueprint=None)
        action.process(blueprint=None)
        action.quit()
        action.enter(facility=None)
        action.process(blueprint=None)
        action.process(blueprint=None)
        action.quit()
        action.end()

    def test_loader_unknown_class(self):

        with self.assertRaises(ImportError):
            PlumberyActionLoader.load('*123*')

    def test_getters(self):
        action = PlumberyActionLoader.load('noop', {'parameter': 'ok'})
        self.assertEqual(action.get_label(), 'noop')
        self.assertEqual(action.get_parameter('parameter'), 'ok')

        parameters = PlumberyParameters({'goofy': 'ok'})
        action = PlumberyActionLoader.load('noop', parameters)
        self.assertEqual(action.get_label(), 'noop')
        self.assertEqual(action.get_parameter('goofy'), 'ok')

    def test_static_load(self):

        actions = ('ansible',
                   'build',
                   'configure',
                   'destroy',
                   'information',
                   'noop',
                   'ping',
                   'prepare',
                   'start',
                   'stop',
                   'wipe',
                  )

        for label in actions:
            action = PlumberyActionLoader.load(label, {})
            self.assertEqual(action.get_label(), label)
            action.begin(engine=None)
            action.enter(facility=None)
            action.process(blueprint=None)
            action.process(blueprint=None)
            action.quit()
            action.enter(facility=None)
            action.process(blueprint=None)
            action.process(blueprint=None)
            action.quit()
            action.enter(facility=None)
            action.process(blueprint=None)
            action.process(blueprint=None)
            action.quit()
            action.end()

    def test_dynamic_load(self):

        actions = PlumberyActionLoader.load_all()

        expected = ['ansible',
                   'build',
                   'configure',
                   'destroy',
                   'information',
                   'inventory',
                   'noop',
                   'ping',
                   'prepare',
                   'start',
                   'stop',
                   'wipe',
                  ]

        self.assertEqual(sorted(actions.keys()), expected)


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
