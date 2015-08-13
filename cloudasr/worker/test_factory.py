import unittest
from lib import create_worker, Worker

class TestFactory(unittest.TestCase):

    def test_can_create_worker(self):
        worker = create_worker("en-GB", "127.0.0.1", "5678", "ipc:///tmp/master", "ipc:///tmp/recordings-saver")
        self.assertIsInstance(worker, Worker)
