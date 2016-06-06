import unittest
import os
import mock
from plumbery.terraform import Terraform


class TerraformTests(unittest.TestCase):
    @mock.patch('os.getenv', mock.Mock(return_value=None))
    def test_init_no_env(self):
        with self.assertRaises(RuntimeError):
            t = Terraform(os.getcwd())
            t.graph(os.getcwd())

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())