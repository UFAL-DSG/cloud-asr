import unittest
from lib import RecordingsSaver
from cloudasr.test_doubles import SocketSpy
from cloudasr.messages.helpers import *


class TestRecordingsSaver(unittest.TestCase):

    def setUp(self):
        self.model = RecordingsModelSpy()
        self.socket = SocketSpy()
        self.create_socket = lambda: self.socket
        self.saver = RecordingsSaver(self.create_socket, self.model, self.socket.has_next_message)

    def test_saver_saves_recordings_received_via_socket(self):
        self.run_saver([
            createSaverMessage(1, 0, 1, 'en-GB', b'body 1', 44100, [(1.0, 'Hello World 1!')]).SerializeToString(),
            createSaverMessage(2, 0, 2, 'en-GB', b'body 2', 44100, [(1.0, 'Hello World 2!')]).SerializeToString(),
        ])

        self.assertThatSaverSavedRecordings([
            (1, 0, 1, 'en-GB', b'body 1', 44100, [{'confidence': 1.0, 'transcript': 'Hello World 1!'}]),
            (2, 0, 2, 'en-GB', b'body 2', 44100, [{'confidence': 1.0, 'transcript': 'Hello World 2!'}])
        ])

    def run_saver(self, messages):
        self.socket.set_messages(messages)
        self.saver.run()

    def assertThatSaverSavedRecordings(self, recordings):
        self.assertEquals(recordings, self.model.saved_recordings)


class RecordingsModelSpy:

    def __init__(self):
        self.saved_recordings = []

    def save_recording(self, id, part, chunk_id, model, body, frame_rate, alternatives):
        self.saved_recordings.append((id, part, chunk_id, model, body, frame_rate, alternatives))
