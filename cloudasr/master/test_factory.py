import unittest
from lib import create_master, Master

class TestFactory(unittest.TestCase):

    def test_can_create_master(self):
        master = create_master("ipc:///tmp/worker", "ipc:///tmp/frontend", "ipc:///tmp/monitor/")
        self.assertIsInstance(master, Master)
