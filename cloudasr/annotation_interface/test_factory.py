import unittest
from lib import create_recordings_saver, RecordingsSaver

class TestFactory(unittest.TestCase):

    def test_can_create_recordings_saver(self):
        recordings_saver = create_recordings_saver("ipc:///tmp/worker", "/tmp/data")
        self.assertIsInstance(recordings_saver, RecordingsSaver)

