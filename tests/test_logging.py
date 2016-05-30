#!/usr/bin/env python

"""
Tests for `logging` module.

"""

import logging
import unittest

from plumbery.logging import plogging


class TestPlumberyLogging(unittest.TestCase):

    def test_direct(self):
        plogging.setLevel(logging.DEBUG)
        self.assertEqual(plogging.getEffectiveLevel(), logging.DEBUG)
        plogging.debug("hello world -- debug")
        plogging.info("hello world -- info")
        plogging.warning("hello world -- warning")
        plogging.error("hello world -- error")
        plogging.critical("hello world -- critical")
        self.assertEqual(plogging.foundErrors(), True)
        plogging.reset()
        self.assertEqual(plogging.foundErrors(), False)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
