import unittest

from plumbery.polishers.windows import WindowsPolisher


class WindowsPolisherTests(unittest.TestCase):
    def setUp(self):
        self.polisher = WindowsPolisher()