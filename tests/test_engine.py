#!/usr/bin/env python

"""
Tests for `plumbery` module.
"""

import io
import socket
import unittest

from libcloud.common.types import InvalidCredsError

from plumbery.engine import PlumberyEngine

myPlan = """
---
safeMode: True
---
# Frankfurt in Europe
locationId: EU6
regionId: dd-eu

blueprints:

  - myBlueprint:
      domain:
        name: myDC
      ethernet:
        name: myVLAN
        subnet: 10.1.10.0
      nodes:
        - myServer
"""

myFacility = {
    'regionId': 'dd-eu',
    'locationId': 'EU7',
    'blueprints': [{
            'fake': {
                    'domain': {
                            'name': 'VDC1',
                            'service': 'ADVANCED',
                            'description': 'fake'},
                    'ethernet': {
                            'name': 'vlan1',
                            'subnet': '10.0.10.0',
                            'description': 'fake'},
                     'nodes': [{
                            'stackstorm': {
                                    'description': 'fake',
                                    'appliance': 'RedHat 6 64-bit 4 CPU'
                                    }
                            }]
                    }
            }]
    }


class FakeLocation:

    id = 'EU7'
    name = 'data centre in Amsterdam'
    country = 'Netherlands'


class TestPlumberyEngine(unittest.TestCase):

    def test_configure(self):

        settings = {
            'safeMode': False,
            'polishers': [
                {'ansible': {}},
                {'spit': {}},
                ]
            }

        self.engine = PlumberyEngine()
        self.engine.set_shared_secret('fake_secret')
        self.assertEqual(self.engine.get_shared_secret(), 'fake_secret')

        self.engine.set_user_name('fake_name')
        self.assertEqual(self.engine.get_user_name(), 'fake_name')

        self.engine.set_user_password('fake_password')
        self.assertEqual(self.engine.get_user_password(), 'fake_password')

        self.engine.configure(settings)
        self.assertEqual(self.engine.safeMode, False)

        try:
            self.engine.setup(io.TextIOWrapper(io.BytesIO(myPlan)))
            self.engine.add_facility(myFacility)
            self.assertEqual(len(self.engine.facilities), 2)

        except socket.gaierror:
            pass
        except InvalidCredsError:
            pass

    def test_lifecycle(self):

        self.engine = PlumberyEngine()
        self.engine.set_shared_secret('fake_secret')
        self.assertEqual(self.engine.get_shared_secret(), 'fake_secret')

        self.engine.set_user_name('fake_name')
        self.assertEqual(self.engine.get_user_name(), 'fake_name')

        self.engine.set_user_password('fake_password')
        self.assertEqual(self.engine.get_user_password(), 'fake_password')

        try:
            self.engine.build_all_blueprints()
            self.engine.build_blueprint('myBlueprint')

            self.engine.start_all_nodes()
            self.engine.start_nodes('myBlueprint')

            self.engine.stop_all_nodes()
            self.engine.stop_nodes('myBlueprint')

            self.engine.destroy_all_nodes()
            self.engine.destroy_nodes('myBlueprint')

        except socket.gaierror:
            pass
        except InvalidCredsError:
            pass

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
