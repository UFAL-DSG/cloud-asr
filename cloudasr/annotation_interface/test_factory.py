import unittest
from lib import create_recordings_saver, create_db_connection, RecordingsSaver

class TestFactory(unittest.TestCase):

    def test_can_create_recordings_saver(self):
        db = create_db_connection("/tmp/db")
        recordings_saver = create_recordings_saver("ipc:///tmp/worker", "/tmp/data", db)
        self.assertIsInstance(recordings_saver, RecordingsSaver)

