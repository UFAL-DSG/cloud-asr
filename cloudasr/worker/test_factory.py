import unittest
from lib import create_worker, Worker

class TestFactory(unittest.TestCase):

    def test_can_create_worker(self):
        worker = create_worker("en-GB", "ipc:///tmp/frontend", "ipc:///tmp/public", "ipc:///tmp/master")
        self.assertIsInstance(worker, Worker)
