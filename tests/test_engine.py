#!/usr/bin/env python

"""
Tests for `plumbery` module.
"""

import logging
import os
import socket
import unittest

from Crypto.PublicKey import RSA
import ast

from mock_api import DimensionDataMockHttp
from libcloud.compute.drivers.dimensiondata import DimensionDataNodeDriver
from libcloud.common.types import InvalidCredsError

from plumbery.__main__ import parse_args, main
from plumbery.engine import PlumberyEngine
from plumbery import __version__

DIMENSIONDATA_PARAMS = ('user', 'password')

myPlan = """
---
safeMode: False

information:
  - hello
  - world

links:
  documentation: "http://www.acme.com/"

defaults:

  domain:
    ipv4: auto

  cloud-config:

    disable_root: false
    ssh_pwauth: true
    ssh_keys:
      rsa_private: |
        {{ pair1.rsa_private }}

      rsa_public: "{{ pair1.ssh.rsa_public }}"

parameters:

  locationId:
    information:
      - "the target data centre for this deployment"
    type: locations.list
    default: EU6

  domainName:
    information:
      - "the name of the network domain to be deployed"
    type: str
    default: myDC

  networkName:
    information:
      - "the name of the Ethernet VLAN to be deployed"
    type: str
    default: myVLAN

---
# Frankfurt in Europe
locationId: "{{ locationId.parameter }}"
regionId: dd-eu

blueprints:

  - myBlueprint:
      domain:
        name: "{{ domainName.parameter }}"
      ethernet:
        name: "{{ networkName.parameter }}"
        subnet: 10.1.10.0
      nodes:
        - myServer:
"""

myFacility = {
    'regionId': 'dd-na',
    'locationId': 'NA9',
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

    def test_init(self):

        engine = PlumberyEngine()
        engine.from_text(myPlan)

        self.assertEqual(engine.safeMode, False)

        self.assertEqual(len(engine.information), 2)

        self.assertEqual(len(engine.links), 1)

        domain = engine.get_default('domain')
        self.assertEqual(domain['ipv4'], 'auto')

        cloudConfig = engine.get_default('cloud-config', {})
        self.assertEqual(len(cloudConfig.keys()), 3)

        parameter = engine.get_parameter('locationId')
        self.assertEqual(parameter, 'EU6')

        parameter = engine.get_parameter('domainName')
        self.assertEqual(parameter, 'myDC')

        parameter = engine.get_parameter('networkName')
        self.assertEqual(parameter, 'myVLAN')

        self.assertEqual(len(engine.facilities), 1)
        facility = engine.facilities[0]
        self.assertEqual(facility.settings['locationId'], 'EU6')
        self.assertEqual(facility.settings['regionId'], 'dd-eu')
        blueprint = facility.blueprints[0]['myBlueprint']
        self.assertEqual(blueprint['domain']['name'], 'myDC')
        self.assertEqual(blueprint['ethernet']['name'], 'myVLAN')

    def test_set(self):

        settings = {
            'safeMode': False,
            'polishers': [
                {'ansible': {}},
                {'spit': {}},
                ]
            }

        engine = PlumberyEngine()
        DimensionDataNodeDriver.connectionCls.conn_classes = (
            None, DimensionDataMockHttp)
        DimensionDataMockHttp.type = None
        self.region = DimensionDataNodeDriver(*DIMENSIONDATA_PARAMS)

        engine.set_shared_secret('fake_secret')
        self.assertEqual(engine.get_shared_secret(), 'fake_secret')

        random = engine.get_secret('random')
        self.assertEqual(len(random), 9)
        self.assertEqual(engine.get_secret('random'), random)

        engine.set_user_name('fake_name')
        self.assertEqual(engine.get_user_name(), 'fake_name')

        engine.set_user_password('fake_password')
        self.assertEqual(engine.get_user_password(), 'fake_password')

        engine.set(settings)
        self.assertEqual(engine.safeMode, False)

        engine.add_facility(myFacility)
        self.assertEqual(len(engine.facilities), 1)

    def test_lifecycle(self):

        engine = PlumberyEngine()
        DimensionDataNodeDriver.connectionCls.conn_classes = (
            None, DimensionDataMockHttp)
        DimensionDataMockHttp.type = None
        self.region = DimensionDataNodeDriver(*DIMENSIONDATA_PARAMS)

        engine.set_shared_secret('fake_secret')
        engine.set_user_name('fake_name')
        engine.set_user_password('fake_password')

        engine.do('build')
        engine.build_all_blueprints()
        engine.build_blueprint('myBlueprint')

        engine.do('start')
        engine.start_all_blueprints()
        engine.start_blueprint('myBlueprint')

        engine.do('polish')
        engine.polish_all_blueprints()
        engine.polish_blueprint('myBlueprint')

        engine.do('stop')
        engine.stop_all_blueprints()
        engine.stop_blueprint('myBlueprint')

        engine.wipe_all_blueprints()
        engine.wipe_blueprint('myBlueprint')

        engine.do('destroy')
        engine.destroy_all_blueprints()
        engine.destroy_blueprint('myBlueprint')

        banner = engine.document_elapsed()
        self.assertEqual('Worked for you' in banner, True)

    def test_as_library(self):

        engine = PlumberyEngine(myFacility)
        DimensionDataNodeDriver.connectionCls.conn_classes = (
            None, DimensionDataMockHttp)
        DimensionDataMockHttp.type = None
        self.region = DimensionDataNodeDriver(*DIMENSIONDATA_PARAMS)

        engine.set_shared_secret('fake_secret')
        engine.set_user_name('fake_name')
        engine.set_user_password('fake_password')

        facilities = engine.list_facility('NA9')
        self.assertEqual(len(facilities), 1)

        facility = facilities[0]
        self.assertEqual(facility.get_setting('regionId'), 'dd-na')
        self.assertEqual(facility.get_setting('locationId'), 'NA9')

        blueprint = facility.get_blueprint('fake')
        self.assertEqual(blueprint.keys(),
                         ['ethernet', 'domain', 'nodes', 'target'])

        engine.do('deploy')
        engine.do('refresh')
        engine.do('dispose')

    def test_lookup(self):

        engine = PlumberyEngine()
        self.assertEqual(engine.lookup('plumbery.version'), __version__)

        engine.secrets = {}
        random = engine.lookup('random.secret')
        self.assertEqual(len(random), 9)
        self.assertEqual(engine.lookup('random.secret'), random)

        md5 = engine.lookup('random.md5.secret')
        self.assertEqual(len(md5), 32)
        self.assertNotEqual(md5, random)

        sha = engine.lookup('random.sha1.secret')
        self.assertEqual(len(sha), 40)
        self.assertNotEqual(sha, random)

        sha = engine.lookup('random.sha256.secret')
        self.assertEqual(len(sha), 64)
        self.assertNotEqual(sha, random)

        id1 = engine.lookup('id1.uuid')
        self.assertEqual(len(id1), 36)
        self.assertEqual(engine.lookup('id1.uuid'), id1)
        id2 = engine.lookup('id2.uuid')
        self.assertEqual(len(id2), 36)
        self.assertNotEqual(id1, id2)

        engine.lookup('application.secret')
        engine.lookup('database.secret')
        engine.lookup('master.secret')
        engine.lookup('slave.secret')

        original = 'hello world'
        text = engine.lookup('pair1.rsa_public')
        self.assertEqual(text.startswith('ssh-rsa '), True)
        key = RSA.importKey(text)
        encrypted = key.publickey().encrypt(original, 32)

        privateKey = engine.lookup('pair1.rsa_private')
        self.assertEqual(privateKey.startswith(
            '-----BEGIN RSA PRIVATE KEY-----'), True)
        key = RSA.importKey(engine.lookup('pair1.rsa_private'))
        decrypted = key.decrypt(ast.literal_eval(str(encrypted)))
        self.assertEqual(decrypted, original)

        self.assertEqual(len(engine.secrets), 12)

        with self.assertRaises(LookupError):
            localKey = engine.lookup('local.rsa_private')

        localKey = engine.lookup('local.rsa_public')
        try:
            path = '~/.ssh/id_rsa.pub'
            with open(os.path.expanduser(path)) as stream:
                text = stream.read()
                stream.close()
                self.assertEqual(localKey.strip(), text.strip())
                logging.info("Successful lookup of local public key")

        except IOError:
            pass

    def test_secrets(self):

        engine = PlumberyEngine()
        engine.secrets = {'hello': 'world'}
        engine.save_secrets(plan='test_engine.yaml')
        self.assertEqual(os.path.isfile('.test_engine.secrets'), True)
        engine.secrets = {}
        engine.load_secrets(plan='test_engine.yaml')
        self.assertEqual(engine.secrets['hello'], 'world')
        engine.forget_secrets(plan='test_engine.yaml')
        self.assertEqual(os.path.isfile('.test_engine.secrets'), False)

    def test_parser(self):

        args = parse_args(['fittings.yaml', 'build', 'web'])
        self.assertEqual(args.fittings, 'fittings.yaml')
        self.assertEqual(args.action, 'build')
        self.assertEqual(args.blueprints, ['web'])
        self.assertEqual(args.facilities, None)
        args = parse_args(['fittings.yaml', 'build', 'web', '-s'])
        self.assertEqual(args.safe, True)
        args = parse_args(['fittings.yaml', 'build', 'web', '-d'])
        self.assertEqual(args.debug, True)
        self.assertEqual(
            logging.getLogger().getEffectiveLevel(), logging.DEBUG)
        args = parse_args(['fittings.yaml', 'build', 'web', '-q'])
        self.assertEqual(args.quiet, True)
        self.assertEqual(
            logging.getLogger().getEffectiveLevel(), logging.WARNING)
        args = parse_args(['fittings.yaml', 'start', '@NA12'])
        self.assertEqual(args.fittings, 'fittings.yaml')
        self.assertEqual(args.action, 'start')
        self.assertEqual(args.blueprints, None)
        self.assertEqual(args.facilities, ['NA12'])
        args = parse_args([
            'fittings.yaml', 'prepare', 'web', 'sql', '@NA9', '@NA12'])
        self.assertEqual(args.fittings, 'fittings.yaml')
        self.assertEqual(args.action, 'prepare')
        self.assertEqual(args.blueprints, ['web', 'sql'])
        self.assertEqual(args.facilities, ['NA9', 'NA12'])
        args = parse_args([
            'fittings.yaml', 'prepare', 'web', '@NA9', 'sql', '@NA12'])
        self.assertEqual(args.fittings, 'fittings.yaml')
        self.assertEqual(args.action, 'prepare')
        self.assertEqual(args.blueprints, ['web', 'sql'])
        self.assertEqual(args.facilities, ['NA9', 'NA12'])
        args = parse_args(['fittings.yaml', 'polish'])
        self.assertEqual(args.fittings, 'fittings.yaml')
        self.assertEqual(args.action, 'polish')
        self.assertEqual(args.blueprints, None)
        self.assertEqual(args.facilities, None)

    def test_main(self):

        engine = PlumberyEngine()
        engine.from_text(myPlan)
        engine.set_user_name('fake_name')
        engine.set_user_password('fake_password')
        with self.assertRaises(SystemExit):
            main(['bad args'], engine)
        with self.assertRaises(SystemExit):
            main(['fittings.yaml'], engine)
        with self.assertRaises(SystemExit):
            main(['fittings.yaml', 'xyz123', 'web'], engine)
        with self.assertRaises(SystemExit):
            main(['-v'], engine)
        with self.assertRaises(SystemExit):
            main(['fittings.yaml', 'build', 'web', '-v'], engine)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
