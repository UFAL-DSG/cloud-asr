import unittest
from lib import RecordingsSaver
from cloudasr.test_doubles import SocketSpy
from cloudasr.messages.helpers import *


class TestRecordingsSaver(unittest.TestCase):

    def setUp(self):
        self.file_saver = FileSaverSpy()
        self.socket = SocketSpy()
        self.saver = RecordingsSaver(self.socket, self.file_saver, self.socket.has_next_message)

    def test_saver_saves_recordings_received_via_socket(self):
        self.run_saver([
            createSaverMessage(1, 'en-GB', b'body 1', 44100, [(1.0, 'Hello World 1!')]),
            createSaverMessage(2, 'en-GB', b'body 2', 44100, [(1.0, 'Hello World 2!')]),
        ])

        self.assertThatSaverSavedRecordings([
            (1, 'en-GB', b'body 1', 44100, [(1.0, 'Hello World 1!')]),
            (2, 'en-GB', b'body 2', 44100, [(1.0, 'Hello World 2!')])
        ])

    def run_saver(self, messages):
        self.socket.set_messages(messages)
        self.saver.run()

    def assertThatSaverSavedRecordings(self, recordings):
        self.assertEquals(recordings, self.file_saver.saved_recordings)


class FileSaverSpy:

    def __init__(self):
        self.saved_recordings = []

    def save(self, id, model, body, frame_rate, alternatives):
        self.saved_recordings.append((id, model, body, frame_rate, alternatives))
