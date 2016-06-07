import unittest
from mock import MagicMock
import plumbery.polishers.monitoring as monitoring
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


class MonitoringConfigurationTests(unittest.TestCase):
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

    def test_monitoring_validation_valid(self):
        settings = {
            'monitoring': 'essentials'
        }
        config = monitoring.MonitoringConfiguration(engine=None, facility=None)
        self.assertTrue(config.validate(settings))

    def test_monitoring_validation_invalid(self):
        settings = {
            'monitoring': 'potato'
        }
        config = monitoring.MonitoringConfiguration(engine=None, facility=None)
        with self.assertRaises(ConfigurationError):
            config.validate(settings)

    def test_monitoring_configuration(self):
        settings = {
            'monitoring': 'essentials',
        }
        config = monitoring.MonitoringConfiguration(engine=None, facility=None)
        node = TestNode()
        config._start_monitoring = MagicMock(return_value=True)
        config.configure(node, settings)
        self.assertTrue(config)
        config._start_monitoring.assert_called_with(node, 'ESSENTIALS')

    def test_monitoring_configuration_deep(self):
        settings = {
            'monitoring': 'essentials',
        }
        config = monitoring.MonitoringConfiguration(engine=self.plumbery,
                                                    facility=self.facility)
        node = TestNode()
        config.configure(node, settings)
        self.assertTrue(config)

    def test_monitoring_deconfiguration(self):
        settings = {
            'monitoring': 'essentials',
        }
        config = monitoring.MonitoringConfiguration(engine=None, facility=None)
        node = TestNode()
        config._stop_monitoring = MagicMock(return_value=True)
        config.deconfigure(node, settings)
        self.assertTrue(config)
        config._stop_monitoring.assert_called_with(node, settings)

    def test_monitoring_deconfiguration_deep(self):
        settings = {
            'monitoring': 'essentials',
        }
        config = monitoring.MonitoringConfiguration(engine=self.plumbery,
                                                    facility=self.facility)
        node = TestNode()
        config.deconfigure(node, settings)
        self.assertTrue(config)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
