import unittest
from lib import create_recordings_saver, RecordingsSaver
from cloudasr.schema import db
from cloudasr.models import WorkerTypesModel, RecordingsModel

class TestFactory(unittest.TestCase):

    def test_can_create_recordings_saver(self):
        worker_types_model = WorkerTypesModel(db)
        recordings_model = RecordingsModel(db, worker_types_model, "/tmp/data", "localhost")
        recordings_saver = create_recordings_saver("ipc:///tmp/worker", recordings_model)
        self.assertIsInstance(recordings_saver, RecordingsSaver)

