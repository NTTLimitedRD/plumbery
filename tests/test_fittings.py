#!/usr/bin/env python

"""
Tests for `fittings` module.
"""

import unittest

from plumbery.fitting import PlumberyFitting, PlumberyFittingLoader


class TestPlumberyFitting(unittest.TestCase):

    def test_loader_ok(self):

        fitting = PlumberyFittingLoader.from_shelf('dummy', {'dummy': 'no'})
        self.assertTrue(isinstance(fitting, PlumberyFitting))

    def test_loader_unknown_class(self):

        with self.assertRaises(ImportError):
            fitting = PlumberyFittingLoader.from_shelf('*123*', {'dummy': 'no'})

    def test_loader_invalid_type(self):

        with self.assertRaises(TypeError):
            fitting = PlumberyFittingLoader.from_shelf('dummy', ('dummy', 'no'))

    def test_loader_invalid_key(self):

        with self.assertRaises(ValueError):
            fitting = PlumberyFittingLoader.from_shelf('dummy', {'*123*': 'no'})

    def test_loader_invalid_value(self):

        with self.assertRaises(TypeError):
            fitting = PlumberyFittingLoader.from_shelf('dummy', {'dummy': True})
        with self.assertRaises(ValueError):
            fitting = PlumberyFittingLoader.from_shelf('dummy', {'dummy': ''})

    def test_do_some_action(self):

        fitting = PlumberyFittingLoader.from_shelf('dummy', {'dummy': 'no'})
        self.assertFalse(fitting.completed)
        self.assertTrue(fitting.do('unmanaged_action'))
        self.assertFalse(fitting.completed)
        self.assertTrue(fitting.do('some_action'))
        self.assertTrue(fitting.completed)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
