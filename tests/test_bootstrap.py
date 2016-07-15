#!/usr/bin/env python

"""
Tests for `bootstrap` module.
"""

import unittest
import os
from tempfile import gettempdir
from mock import MagicMock, patch
import requests_mock

import plumbery.bootstrap as b

tempdir = gettempdir()


class BootstrapTests(unittest.TestCase):
    def test_url_cwd(self):
        url = 'http://test.com/fittings.yaml'
        args = b.parse_args([url])
        b.download_file = MagicMock(return_value=True)
        b.main(args)
        b.download_file.assert_called_with(url, os.getcwd())

    def test_url_target_directory(self):
        url = 'http://test.com/fittings.yaml'
        args = b.parse_args([url, '-o', '/tmp'])
        b.download_file = MagicMock(return_value=True)
        b.main(args)
        b.download_file.assert_called_with(url, '/tmp')

    def test_url_manifest(self):
        url = 'http://test.com/manifest.mf'
        args = b.parse_args([url, '-o', '/tmp'])
        b.download_manifest = MagicMock(return_value=True)
        b.main(args)
        b.download_manifest.assert_called_with(url, '/tmp')

    def test_download_manifest(self):
        url = 'http://test.com/manifest.mf'
        b.download_file = MagicMock(return_value='test.file')
        open_name = 'plumbery.bootstrap.open'
        with patch(open_name, create=True) as mock_open:
            mock_open.return_value = MagicMock(return_value='test.file')
            b.download_manifest(url, os.getcwd())
        b.download_file.assert_called_with(url, os.getcwd())

    def test_download_file(self):
        with requests_mock.mock() as m:
            m.get('http://test.com/manifest.mf', text='testing')
            b.download_file('http://test.com/manifest.mf', tempdir)
            with open(os.path.join(tempdir, 'manifest.mf')) as tmp_file:
                self.assertEqual(tmp_file.read(), 'testing')

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
