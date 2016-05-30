import unittest
import plumbery.polishers.cpu as cpu
from plumbery.exception import ConfigurationError


class CpuConfigurationTests(unittest.TestCase):
    def test_cpu_validation_valid(self):
        settings = {
            'cpu': 4
        }
        config = cpu.CpuConfiguration()
        self.assertTrue(config.validate(settings))

    def test_cpu_validation_invalid(self):
        settings = {
            'cpu': 128
        }
        config = cpu.CpuConfiguration()
        with self.assertRaises(ConfigurationError):
            config.validate(settings)

    def test_cpu_configuraiton(self):
        settings = {
            'cpu': 4
        }
        config = cpu.CpuConfiguration()
        cpuSetup = config.configure(None, settings)
        self.assertEquals(int(cpuSetup.cpu_count), 4)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())