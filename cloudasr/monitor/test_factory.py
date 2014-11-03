import unittest
from lib import create_monitor, Monitor

class TestFactory(unittest.TestCase):

    def test_can_create_monitor(self):
        monitor = create_monitor("ipc:///tmp/worker", lambda x: x)
        self.assertIsInstance(monitor, Monitor)
