import unittest
from lib import create_frontend_worker, FrontendWorker

class TestFactory(unittest.TestCase):

    def test_can_create_frontend_worker(self):
        worker = create_frontend_worker("ipc:///tmp/worker")
        self.assertIsInstance(worker, FrontendWorker)
