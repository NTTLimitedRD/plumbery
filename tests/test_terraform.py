#!/usr/bin/env python

"""
Tests for `terraform` module.
"""

import unittest
import os
import mock

from plumbery.terraform import Terraform

from tempfile import gettempdir
tempdir = gettempdir()


class TerraformTests(unittest.TestCase):
    @mock.patch('os.getenv', mock.Mock(return_value=None))
    def test_init_no_env(self):
        with self.assertRaises(RuntimeError):
            t = Terraform(os.getcwd())
            t.graph(os.getcwd())

    def test_build(self):
        t = Terraform(tempdir)
        t._run_tf = mock.MagicMock(return_value=(2, "", ""))
        t.build({})
        t._run_tf.assert_called_with("apply", os.path.join(tempdir, '.tfstate'))

    def test_destroy(self):
        t = Terraform(tempdir)
        t._run_tf = mock.MagicMock(return_value=(2, "", ""))
        t.destroy({})
        t._run_tf.assert_called_with("plan", tempdir, destroy=True, detailed_exitcode=True, input=False,
                                     var_file=os.path.join(tempdir, '.tfvars'))

    def test_graph(self):
        t = Terraform(tempdir)
        t._run_tf = mock.MagicMock(return_value=(2, "", ""))
        t.graph(tempdir)
        t._run_tf.assert_called_with("graph", tempdir)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())