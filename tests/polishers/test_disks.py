import unittest
import plumbery.polishers.disks as disks
from plumbery.exception import ConfigurationError
from plumbery.engine import PlumberyEngine
from plumbery.facility import PlumberyFacility


class DiskConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.engine = PlumberyEngine()
        self.facility = PlumberyFacility(self.engine)

    def test_disk_validation_valid(self):
        settings = {
            'disks': ["1 100 Standard"]
        }
        config = disks.DisksConfiguration(engine=self.engine, facility=self.facility)
        self.assertTrue(config.validate(settings))

    def test_disk_validation_invalid(self):
        settings = {
            'disks': "cabbages"
        }
        config = disks.DisksConfiguration(engine=self.engine, facility=self.facility)
        with self.assertRaises(ConfigurationError):
            config.validate(settings)

    def test_disk_validation_invalid_too_small(self):
        settings = {
            'disks': ["1 1 Standard"]
        }
        config = disks.DisksConfiguration(engine=self.engine, facility=self.facility)
        with self.assertRaises(ConfigurationError):
            config.validate(settings)

    def test_disk_validation_invalid_too_large(self):
        settings = {
            'disks': ["1 3000 Standard"]
        }
        config = disks.DisksConfiguration(engine=self.engine, facility=self.facility)
        with self.assertRaises(ConfigurationError):
            config.validate(settings)

    def test_disk_validation_invalid_scsi(self):
        settings = {
            'disks': ["12 100 Standard"]
        }
        config = disks.DisksConfiguration(engine=self.engine, facility=self.facility)
        with self.assertRaises(ConfigurationError):
            config.validate(settings)

    def test_disk_validation_invalid_tier(self):
        settings = {
            'disks': ["1 100 potato"]
        }
        config = disks.DisksConfiguration(engine=self.engine, facility=self.facility)
        with self.assertRaises(ConfigurationError):
            config.validate(settings)

    def test_disk_configuraiton_tier(self):
        settings = {
            'disks': ["1 100 Standard"]
        }
        config = disks.DisksConfiguration(engine=self.engine, facility=self.facility)
        diskSetup = config.configure(None, settings)
        self.assertTrue(diskSetup)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())