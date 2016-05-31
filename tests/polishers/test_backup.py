import unittest
import plumbery.polishers.backup as backup
from plumbery.exception import ConfigurationError
from tests.mock_api import DimensionDataMockHttp
from libcloud.compute.drivers.dimensiondata import DimensionDataNodeDriver
from plumbery.engine import PlumberyEngine
from plumbery.facility import PlumberyFacility

DIMENSIONDATA_PARAMS = ('user', 'password')

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


class TestNode(object):
    id = 'e75ead52-692f-4314-8725-c8a4f4d13a87'
    name = 'test'


class BackupConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.plumbery = PlumberyEngine()
        self.plumbery.set_user_name('fake_user')
        self.plumbery.set_user_password('fake_password')
        DimensionDataNodeDriver.connectionCls.conn_classes = (
            None, DimensionDataMockHttp)
        DimensionDataMockHttp.type = None
        self.plumbery.region = DimensionDataNodeDriver(*DIMENSIONDATA_PARAMS)
        self.facility = PlumberyFacility(
            plumbery=self.plumbery, fittings=myFacility)
        self.facility.power_on()

    def test_backup_validation_valid(self):
        settings = {
            'backup': 'essentials'
        }
        config = backup.BackupConfiguration(engine=None, facility=None)
        self.assertTrue(config.validate(settings))

    def test_backup_validation_invalid(self):
        settings = {
            'backup': 'potato'
        }
        config = backup.BackupConfiguration(engine=None, facility=None)
        with self.assertRaises(ConfigurationError):
            config.validate(settings)

    def test_backup_configuration(self):
        settings = {
            'backup': 'essentials',
        }
        config = backup.BackupConfiguration(self.plumbery, self.facility)
        backupConfiguration = config.configure(TestNode(), settings)
        self.assertTrue(backupConfiguration)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
