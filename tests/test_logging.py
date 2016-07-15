#!/usr/bin/env python

"""
Tests for `plogging` module.

"""

import logging
import unittest

from plumbery.plogging import plogging


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

    def test_alien(self):
        logger = logging.getLogger('alien.from.mars')
        logger.setLevel(logging.DEBUG)
        logger.debug("hello mars -- debug")
        logger.info("hello mars -- info")
        logger.warning("hello mars -- warning")
        logger.error("hello mars -- error")
        logger.critical("hello mars -- critical")

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
