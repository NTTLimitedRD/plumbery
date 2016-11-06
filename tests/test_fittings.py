#!/usr/bin/env python

"""
Tests for `fittings` module.
"""

import unittest

from plumbery.fitting import PlumberyFitting, PlumberyFittingLoader


class TestPlumberyFitting(unittest.TestCase):

    def test_loader_unknown_class(self):

        with self.assertRaises(ImportError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='*123*',
                engine=None,
                facility=None,
                settings={'dummy': 'no'})

    def test_dummy(self):

        fitting = PlumberyFittingLoader.from_shelf(
            label='dummy',
            engine=None,
            facility=None,
            settings={'dummy': 'no'})
        self.assertTrue(isinstance(fitting, PlumberyFitting))
        self.assertFalse(fitting.completed)
        self.assertTrue(fitting.do('unmanaged_action'))
        self.assertFalse(fitting.completed)
        self.assertTrue(fitting.do('some_action'))
        self.assertTrue(fitting.completed)

        with self.assertRaises(TypeError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='dummy',
                engine=None,
                facility=None,
                settings=('dummy', 'no'))

        with self.assertRaises(KeyError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='dummy',
                engine=None,
                facility=None,
                settings={})

        with self.assertRaises(KeyError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='dummy',
                engine=None,
                facility=None,
                settings={'*123*': 'no'})

        with self.assertRaises(TypeError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='dummy',
                engine=None,
                facility=None,
                settings={'dummy': True})

        with self.assertRaises(ValueError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='dummy',
                engine=None,
                facility=None,
                settings={'dummy': ''})

    def test_domain(self):

        # minimum viable settings

        fitting = PlumberyFittingLoader.from_shelf(
            label='domain',
            engine=None,
            facility=None,
            settings={'name': 'vdc1'})
        self.assertTrue(isinstance(fitting, PlumberyFitting))
        self.assertEqual(fitting.label, 'domain')
        self.assertEqual(fitting.description, '#plumbery')
        self.assertEqual(fitting.ipv4, None)
        self.assertEqual(fitting.name, 'vdc1')
        self.assertEqual(fitting.service, 'ESSENTIALS')

        with self.assertRaises(TypeError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='domain',
                engine=None,
                facility=None,
                settings=('domain', 'ipv4'))

        with self.assertRaises(KeyError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='domain',
                engine=None,
                facility=None,
                settings={'*123*': 'no'})

        # description

        fitting = PlumberyFittingLoader.from_shelf(
            label='domain',
            engine=None,
            facility=None,
            settings={'name': 'vdc1', 'description': 'hello'})
        self.assertEqual(fitting.description, 'hello #plumbery')

        with self.assertRaises(TypeError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='domain',
                engine=None,
                facility=None,
                settings={'name': 'vdc1', 'description': True})

        with self.assertRaises(ValueError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='domain',
                engine=None,
                facility=None,
                settings={'name': 'vdc1', 'description': ''})

        # ipv4

        fitting = PlumberyFittingLoader.from_shelf(
            label='domain',
            engine=None,
            facility=None,
            settings={'name': 'vdc1', 'ipv4': 'auto'})
        self.assertEqual(fitting.ipv4, 'auto')

        fitting = PlumberyFittingLoader.from_shelf(
            label='domain',
            engine=None,
            facility=None,
            settings={'name': 'vdc1', 'ipv4': 6})
        self.assertEqual(fitting.ipv4, 6)

        with self.assertRaises(TypeError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='domain',
                engine=None,
                facility=None,
                settings={'name': 'vdc1', 'ipv4': True})

        with self.assertRaises(ValueError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='domain',
                engine=None,
                facility=None,
                settings={'name': 'vdc1', 'ipv4': -2})

        with self.assertRaises(ValueError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='domain',
                engine=None,
                facility=None,
                settings={'name': 'vdc1', 'ipv4': 321})

        # name

        with self.assertRaises(KeyError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='domain',
                engine=None,
                facility=None,
                settings={'description': 'test', 'ipv4': 6})

        with self.assertRaises(TypeError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='domain',
                engine=None,
                facility=None,
                settings={'name': True, 'ipv4': 'auto'})

        with self.assertRaises(ValueError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='domain',
                engine=None,
                facility=None,
                settings={'name': ''})

        # service

        fitting = PlumberyFittingLoader.from_shelf(
            label='domain',
            engine=None,
            facility=None,
            settings={'name': 'vdc1', 'service': 'essentials'})
        self.assertEqual(fitting.service, 'ESSENTIALS')

        fitting = PlumberyFittingLoader.from_shelf(
            label='domain',
            engine=None,
            facility=None,
            settings={'name': 'vdc1', 'service': 'ESSENTIALS'})
        self.assertEqual(fitting.service, 'ESSENTIALS')

        fitting = PlumberyFittingLoader.from_shelf(
            label='domain',
            engine=None,
            facility=None,
            settings={'name': 'vdc1', 'service': 'advanced'})
        self.assertEqual(fitting.service, 'ADVANCED')

        fitting = PlumberyFittingLoader.from_shelf(
            label='domain',
            engine=None,
            facility=None,
            settings={'name': 'vdc1', 'service': 'ADVANCED'})
        self.assertEqual(fitting.service, 'ADVANCED')

        with self.assertRaises(TypeError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='domain',
                engine=None,
                facility=None,
                settings={'name': 'vdc1', 'service': True})

        with self.assertRaises(ValueError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='domain',
                engine=None,
                facility=None,
                settings={'name': 'vdc1', 'service': '*123*'})

    def test_ethernet(self):

        # minimum viable settings

        fitting = PlumberyFittingLoader.from_shelf(
            label='ethernet',
            engine=None,
            facility=None,
            settings={'name': 'vlan1', 'subnet': '10.2.3.0'})
        self.assertTrue(isinstance(fitting, PlumberyFitting))
        self.assertEqual(fitting.label, 'ethernet')
        self.assertEqual(fitting.description, '#plumbery')
        self.assertEqual(fitting.name, 'vlan1')
        self.assertEqual(fitting.subnet, '10.2.3.0')

        with self.assertRaises(TypeError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='ethernet',
                engine=None,
                facility=None,
                settings=('description', 'subnet'))

        with self.assertRaises(KeyError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='ethernet',
                engine=None,
                facility=None,
                settings={'*123*': 'no'})

        # description

        fitting = PlumberyFittingLoader.from_shelf(
            label='ethernet',
            engine=None,
            facility=None,
            settings={'name': 'vlan1', 'description': 'hello', 'subnet': '10.2.3.0'})
        self.assertEqual(fitting.description, 'hello #plumbery')

        with self.assertRaises(TypeError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='ethernet',
                engine=None,
                facility=None,
                settings={'name': 'vlan1', 'description': True, 'subnet': '10.2.3.0'})

        with self.assertRaises(ValueError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='ethernet',
                engine=None,
                facility=None,
                settings={'name': 'vlan1', 'description': '', 'subnet': '10.2.3.0'})

        # name

        with self.assertRaises(KeyError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='ethernet',
                engine=None,
                facility=None,
                settings={'description': 'test', 'subnet': '10.2.3.0'})

        with self.assertRaises(TypeError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='ethernet',
                engine=None,
                facility=None,
                settings={'name': True, 'subnet': '10.2.3.0'})

        with self.assertRaises(ValueError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='ethernet',
                engine=None,
                facility=None,
                settings={'name': '', 'subnet': '10.2.3.0'})

        # subnet

        fitting = PlumberyFittingLoader.from_shelf(
            label='ethernet',
            engine=None,
            facility=None,
            settings={'name': 'vlan1', 'subnet': '10.2.3.0'})
        self.assertEqual(fitting.subnet, '10.2.3.0')

        fitting = PlumberyFittingLoader.from_shelf(
            label='ethernet',
            engine=None,
            facility=None,
            settings={'name': 'vlan1', 'subnet': '192.6.7.0'})
        self.assertEqual(fitting.subnet, '192.6.7.0')

        with self.assertRaises(TypeError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='ethernet',
                engine=None,
                facility=None,
                settings={'name': 'vlan1', 'subnet': True})

        with self.assertRaises(ValueError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='ethernet',
                engine=None,
                facility=None,
                settings={'name': 'vlan1', 'subnet': '*123*'})

        with self.assertRaises(ValueError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='ethernet',
                engine=None,
                facility=None,
                settings={'name': 'vlan1', 'subnet': '8.8.8'})

        with self.assertRaises(ValueError):
            fitting = PlumberyFittingLoader.from_shelf(
                label='ethernet',
                engine=None,
                facility=None,
                settings={'name': 'vlan1', 'subnet': '8.8.8.8.8'})

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
