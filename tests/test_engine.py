#!/usr/bin/env python

"""
Tests for `plumbery` module.
"""

# special construct to allow relative import
#
if __name__ == "__main__" and __package__ is None:
    __package__ = "tests"
from tests import dummy

import logging
import os
import unittest
import yaml

try:
    from Cryptodome.PublicKey import RSA
    from Cryptodome.Cipher import PKCS1_OAEP
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
    logging.getLogger().error('No Cryptodome support loaded')

import six

if six.PY2:
    b = bytes = ensure_string = str
else:
    def ensure_string(s):
        if isinstance(s, str):
            return s
        elif isinstance(s, bytes):
            return s.decode('utf-8')
        else:
            raise TypeError("Invalid argument %r for ensure_string()" % (s,))

    def b(s):
        if isinstance(s, str):
            return s.encode('utf-8')
        elif isinstance(s, bytes):
            return s
        elif isinstance(s, int):
            return bytes([s])
        else:
            raise TypeError("Invalid argument %r for b()" % (s,))

from libcloud.compute.drivers.dimensiondata import DimensionDataNodeDriver

from plumbery.__main__ import parse_args, main
from plumbery.action import PlumberyAction
from plumbery.engine import PlumberyEngine
from plumbery.plogging import plogging
from plumbery.polisher import PlumberyPolisher
from plumbery import __version__

import requests_mock
from .mock_api import DimensionDataMockHttp
DIMENSIONDATA_PARAMS = ('user', 'password')

myParameters = {

    'locationId': 'NA9',
    'domainName': 'justInTimeDomain',
    'networkName': 'justInTimeNetwork'

    }

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

    write_files:

    runcmd:

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

buildPolisher: alien

polishers:
  - ansible:
      reap: gigafox_ansible.yaml
  - inventory:
      reap: gigafox_inventory.yaml
  - prepare:
      key: ~/.ssh/id_rsa.pub
      reap: gigafox_prepares.yaml

---
# Frankfurt in Europe
locationId: "{{ parameter.locationId }}"
regionId: dd-eu

blueprints:

  - myBlueprint:
      domain:
        name: "{{ parameter.domainName }}"
      ethernet:
        name: "{{ parameter.networkName }}"
        subnet: 10.1.10.0
      nodes:
        - myServer:
"""

myEuropeanPlan = """
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

    hostname: "{{ parameter.nodeName }}"

    packages:
      - ntp

    write_files:

      - path: /root/hosts.awk
        content: |
          #!/usr/bin/awk -f
          /^{{ {{ parameter.nodeName }}.private }}/ {next}
          /^{{ {{ parameter.nodeName }}.ipv6 }}/ {next}
          {print}
          END {
           print "{{ {{ parameter.nodeName }}.private }}    {{ parameter.nodeName }}"
           print "{{ {{ parameter.nodeName }}.ipv6 }}    {{ parameter.nodeName }}"
          }

parameters:

  locationId:
    information:
      - "the target data centre for this deployment"
    type: locations.list
    default: EU8

  regionId:
    information:
      - "the target region for this deployment"
    type: regions.list
    default: dd-eu

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

  nodeName:
    information:
      - "the name of the node to be deployed"
    type: str
    default: myServer

---
locationId: "{{ parameter.locationId }}"
regionId: {{ parameter.regionId }}

blueprints:

  - myBlueprint:
      domain:
        name: "{{ parameter.domainName }}"
      ethernet:
        name: "{{ parameter.networkName }}"
        subnet: 10.1.10.0
      nodes:
        - {{ parameter.nodeName }}:
"""

myAmericanBinding = {
    'locationId': 'NA9',
    'regionId': 'dd-na',
    'nodeName': 'toto'
    }


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


myPrivatePlan = """
---
safeMode: True
apiHost: quasimoto.com
locationId: NA9
blueprints:

  - myBlueprint:
      domain:
        name: myDC
      ethernet:
        accept:
          - NA19::remoteNetwork
      nodes:
        - myServer:
            default: bee
            information:
              - complementary information
            memory: 5
            cloud-config:
              packages:
                - smtp
              runcmd:
                - echo "world"

"""


class FakeLocation:

    id = 'EU7'
    name = 'data centre in Amsterdam'
    country = 'Netherlands'


class FakeAction(PlumberyAction):
    def __init__(self, settings):
        self.count = 3

    def ignite(self, engine):
        self.count += 100

    def enter(self, facility):
        self.count *= 2

    def handle(self, blueprint):
        self.count += 5

    def quit(self):
        self.count -= 2

    def reap(self):
        self.count += 1


class TestPlumberyEngine(unittest.TestCase):

    def test_init(self):

        engine = PlumberyEngine()

        engine.set_fittings(myPlan)

        self.assertEqual(engine.buildPolisher, 'alien')

        domain = engine.get_default('domain')
        self.assertEqual(domain['ipv4'], 'auto')

        cloudConfig = engine.get_default('cloud-config', {})
        self.assertEqual(len(cloudConfig.keys()), 5)

        self.assertEqual(len(engine.information), 2)

        self.assertEqual(len(engine.links), 1)

        parameters = engine.get_parameters()
        self.assertEqual(parameters['parameter.locationId'],
                         'EU6')
        self.assertEqual(parameters['parameter.domainName'],
                         'myDC')
        self.assertEqual(parameters['parameter.networkName'],
                         'myVLAN')

        parameter = engine.get_parameter('locationId')
        self.assertEqual(parameter, 'EU6')

        parameter = engine.get_parameter('domainName')
        self.assertEqual(parameter, 'myDC')

        parameter = engine.get_parameter('networkName')
        self.assertEqual(parameter, 'myVLAN')

        self.assertEqual(len(engine.polishers), 3)
        for polisher in engine.polishers:
            self.assertTrue(isinstance(polisher, PlumberyPolisher))

        self.assertEqual(engine.safeMode, False)

        self.assertEqual(len(engine.facilities), 1)
        facility = engine.facilities[0]
        self.assertEqual(facility.settings['locationId'], 'EU6')
        self.assertEqual(facility.settings['regionId'], 'dd-eu')
        blueprint = facility.blueprints[0]['myBlueprint']
        self.assertEqual(blueprint['domain']['name'], 'myDC')
        self.assertEqual(blueprint['ethernet']['name'], 'myVLAN')

    def test_parameters(self):

        engine = PlumberyEngine()
        engine.set_parameters(myParameters)

        parameters = engine.get_parameters()
        self.assertEqual(parameters['parameter.locationId'],
                         'NA9')
        self.assertEqual(parameters['parameter.domainName'],
                         'justInTimeDomain')
        self.assertEqual(parameters['parameter.networkName'],
                         'justInTimeNetwork')

        engine.set_fittings(myPlan)

        parameters = engine.get_parameters()
        self.assertEqual(parameters['parameter.locationId'],
                         'NA9')
        self.assertEqual(parameters['parameter.domainName'],
                         'justInTimeDomain')
        self.assertEqual(parameters['parameter.networkName'],
                         'justInTimeNetwork')

        self.assertEqual(engine.safeMode, False)

        self.assertEqual(len(engine.information), 2)

        self.assertEqual(len(engine.links), 1)

        domain = engine.get_default('domain')
        self.assertEqual(domain['ipv4'], 'auto')

        cloudConfig = engine.get_default('cloud-config', {})
        self.assertEqual(len(cloudConfig.keys()), 5)

        parameter = engine.get_parameter('locationId')
        self.assertEqual(parameter, 'NA9')

        parameter = engine.get_parameter('domainName')
        self.assertEqual(parameter, 'justInTimeDomain')

        parameter = engine.get_parameter('networkName')
        self.assertEqual(parameter, 'justInTimeNetwork')

        self.assertEqual(len(engine.facilities), 1)
        facility = engine.facilities[0]
        self.assertEqual(facility.settings['locationId'], 'NA9')
        self.assertEqual(facility.settings['regionId'], 'dd-eu')
        blueprint = facility.blueprints[0]['myBlueprint']
        self.assertEqual(blueprint['domain']['name'], 'justInTimeDomain')
        self.assertEqual(blueprint['ethernet']['name'], 'justInTimeNetwork')

    def test_set(self):

        engine = PlumberyEngine()
        DimensionDataNodeDriver.connectionCls.conn_classes = (
            None, DimensionDataMockHttp)
        DimensionDataMockHttp.type = None
        self.region = DimensionDataNodeDriver(*DIMENSIONDATA_PARAMS)

        settings = {
            'safeMode': False,
            'polishers': [
                {'ansible': {}},
                {'configure': {}},
                ]
            }

        engine.set_settings(settings)
        self.assertEqual(engine.safeMode, False)

        engine.add_facility(myFacility)
        self.assertEqual(len(engine.facilities), 1)

        self.assertEqual(engine.get_shared_user(), 'root')
        engine.set_shared_user('ubuntu')
        self.assertEqual(engine.get_shared_user(), 'ubuntu')

        engine.set_shared_secret('fake_secret')
        self.assertEqual(engine.get_shared_secret(), 'fake_secret')

        random = engine.get_secret('random')
        self.assertEqual(len(random), 9)
        self.assertEqual(engine.get_secret('random'), random)

        engine.set_user_name('fake_name')
        self.assertEqual(engine.get_user_name(), 'fake_name')

        engine.set_user_password('fake_password')
        self.assertEqual(engine.get_user_password(), 'fake_password')

    def test_settings_private(self):
        engine = PlumberyEngine()
        engine.set_shared_secret('fake_secret')
        engine.set_user_name('fake_name')
        engine.set_user_password('fake_password')
        engine.set_fittings(myPrivatePlan)
        facilities = engine.list_facility('quasimoto.com')
        self.assertEqual(len(facilities), 1)
        facilities[0].power_on()
#        self.assertEqual(facilities[0].region.connection.host, 'quasimoto.com')

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
        engine.do('build', 'myBlueprint')
        engine.build_blueprint('myBlueprint')

        engine.do('deploy')
        engine.do('deploy', 'myBlueprint')

        engine.do('destroy')
        engine.destroy_all_blueprints()
        engine.do('destroy', 'myBlueprint')
        engine.destroy_blueprint('myBlueprint')

        engine.do('dispose')
        engine.do('dispose', 'myBlueprint')

        engine.do('polish')
        engine.polish_all_blueprints()
        engine.do('polish', 'myBlueprint')
        engine.polish_blueprint('myBlueprint')

        engine.do('secrets')

        engine.do('start')
        engine.start_all_blueprints()
        engine.do('start', 'myBlueprint')
        engine.start_blueprint('myBlueprint')

        engine.do('stop')
        engine.stop_all_blueprints()
        engine.do('stop', 'myBlueprint')
        engine.stop_blueprint('myBlueprint')

        engine.do('wipe')
        engine.wipe_all_blueprints()
        engine.do('wipe', 'myBlueprint')
        engine.wipe_blueprint('myBlueprint')

        banner = engine.document_elapsed()
        self.assertEqual('Worked for you' in banner, True)

    def test_process_all_blueprints(self):

        engine = PlumberyEngine()
        DimensionDataNodeDriver.connectionCls.conn_classes = (
            None, DimensionDataMockHttp)
        DimensionDataMockHttp.type = None
        self.region = DimensionDataNodeDriver(*DIMENSIONDATA_PARAMS)

        engine.set_shared_secret('fake_secret')
        engine.set_user_name('fake_name')
        engine.set_user_password('fake_password')
        engine.set_fittings(myPrivatePlan)

        engine.process_all_blueprints(action='dummy')

        action = FakeAction({})
        engine.process_all_blueprints(action)
        self.assertEqual(action.count, 210)

    def test_process_blueprint(self):

        engine = PlumberyEngine()
        DimensionDataNodeDriver.connectionCls.conn_classes = (
            None, DimensionDataMockHttp)
        DimensionDataMockHttp.type = None
        self.region = DimensionDataNodeDriver(*DIMENSIONDATA_PARAMS)

        engine.set_shared_secret('fake_secret')
        engine.set_user_name('fake_name')
        engine.set_user_password('fake_password')
        engine.set_fittings(myPrivatePlan)

        engine.process_blueprint(action='dummy', names='fake')

        action = FakeAction({})
        engine.process_blueprint(action, names='fake')
        self.assertEqual(action.count, 205)

    def test_as_library(self):

        engine = PlumberyEngine(myEuropeanPlan, myAmericanBinding)
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

        self.assertTrue(facility.get_blueprint('fake') is None)

        blueprint = facility.get_blueprint('myBlueprint')

        node = blueprint['nodes'][0]
        self.assertEqual(list(node)[0], 'toto')

        config = node['toto']['cloud-config']
        self.assertEqual(config['hostname'], 'toto')
        self.assertEqual(config['write_files'][0]['content'].count('toto'), 6)

        engine.do('deploy')
        engine.do('dispose')

    def test_lookup(self):

        engine = PlumberyEngine()
        self.assertEqual(engine.lookup('plumbery.version'), __version__)

        engine.secrets = {}
        random = engine.lookup('secret.random')
        self.assertEqual(len(random), 9)
        self.assertEqual(engine.lookup('secret.random'), random)

        md5 = engine.lookup('secret.random.md5')
        self.assertEqual(len(md5), 32)
        self.assertNotEqual(md5, random)

        sha = engine.lookup('secret.random.sha1')
        self.assertEqual(len(sha), 40)
        self.assertNotEqual(sha, random)

        sha = engine.lookup('secret.random.sha256')
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

        original = b'hello world'
        if HAS_CRYPTO:
            text = engine.lookup('pair1.rsa_public')
            self.assertTrue(ensure_string(text).startswith('ssh-rsa '))
            key = RSA.importKey(text)
            cipher = PKCS1_OAEP.new(key)
            encrypted = cipher.encrypt(original)

            privateKey = engine.lookup('pair1.rsa_private')
            self.assertTrue(ensure_string(privateKey).startswith(
                '-----BEGIN RSA PRIVATE KEY-----'))
            key = RSA.importKey(engine.lookup('pair1.rsa_private'))
            cipher = PKCS1_OAEP.new(key)
            decrypted = cipher.decrypt(encrypted)
            self.assertEqual(decrypted, original)

            token = engine.lookup('https://discovery.etcd.io/new')
            self.assertEqual(token.startswith(
                'https://discovery.etcd.io/'), True)
            self.assertEqual(len(token), 58)

            self.assertEqual(len(engine.secrets), 13)

            with self.assertRaises(LookupError):
                localKey = engine.lookup('local.rsa_private')

            localKey = engine.lookup('rsa_public.local')
            try:
                path = '~/.ssh/id_rsa.pub'
                with open(os.path.expanduser(path)) as stream:
                    text = stream.read()
                    stream.close()
                    self.assertEqual(localKey.strip(), text.strip())
                    plogging.info("Successful lookup of local public key")

            except IOError:
                pass

    def test_secrets(self):

        engine = PlumberyEngine()
        engine.secrets = {'hello': 'world'}
        engine.save_secrets(plan='test_engine.yaml')
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

        args = parse_args(
            ['fittings.yaml', 'build', 'web', '-p', 'parameters.yaml'])
        self.assertEqual(args.parameters, ['parameters.yaml'])

        args = parse_args(
            ['fittings.yaml', 'build', 'web', '-p', 'parameters.yaml', '-s'])
        self.assertEqual(args.parameters, ['parameters.yaml'])
        self.assertEqual(args.safe, True)

        args = parse_args(
            ['fittings.yaml', 'build', 'web', '-p', 'parameters.yaml', '-d'])
        self.assertEqual(args.parameters, ['parameters.yaml'])
        self.assertEqual(args.debug, True)

        args = parse_args(['fittings.yaml', 'build', 'web', '-s'])
        self.assertEqual(args.safe, True)

        args = parse_args(['fittings.yaml', 'build', 'web', '-d'])
        self.assertEqual(args.debug, True)
        self.assertEqual(
            plogging.getEffectiveLevel(), logging.DEBUG)

        args = parse_args(['fittings.yaml', 'build', 'web', '-q'])
        self.assertEqual(args.quiet, True)
        self.assertEqual(
            plogging.getEffectiveLevel(), logging.WARNING)

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

        with self.assertRaises(SystemExit):
            main(['fittings.yaml', 'build', 'web', '@EU6'])

        engine = PlumberyEngine()
        engine.set_fittings(myPlan)
        engine.set_user_name('fake_name')
        engine.set_user_password('fake_password')
        with self.assertRaises(SystemExit):
            main(['-v'], engine)
        with self.assertRaises(SystemExit):
            main(['fittings.yaml', 'build', 'web'], engine)
        with self.assertRaises(SystemExit):
            main(['fittings.yaml', 'build', 'web', '-v'], engine)
        with self.assertRaises(SystemExit):
            main(['fittings.yaml', 'build', 'web', '@EU6'], engine)

    def test_bad_args(self):

        engine = PlumberyEngine()
        engine.set_fittings(myPlan)
        with self.assertRaises(SystemExit):
            main(['bad args'], engine)
        with self.assertRaises(SystemExit):
            main(['fittings.yaml'], engine)
        with self.assertRaises(SystemExit):
            main(['fittings.yaml', 'xyz123', 'web'], engine)
        with self.assertRaises(SystemExit):
            main(['fittings.yaml', 'build', 'web', '@'], engine)

    def test_param_http(self):
        engine = PlumberyEngine()
        with self.assertRaises(TypeError):
            engine.set_parameters(('http://smee.com/params.yml'))

    def test_remote_params(self):
        engine = PlumberyEngine()
        with requests_mock.mock() as m:
            m.get('http://smee.com/params.yml', text=yaml.dump(myParameters))
            engine.set_parameters('http://smee.com/params.yml')

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
