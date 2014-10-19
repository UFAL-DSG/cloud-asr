import unittest
from lib import Monitor
from cloudasr.test_doubles import PollerSpy, SocketSpy
from cloudasr.messages.helpers import *


class TestMonitor(unittest.TestCase):

    def setUp(self):
        self.socket = SocketSpy()
        self.monitor = Monitor(self.socket, self.emit, self.socket.has_next_message)
        self.emmited_messages = []

    def test_monitor_forwards_messages_to_socketio(self):
        messages = [
            createWorkerStatusMessage("tcp://127.0.0.1:1", "en-GB", "WAITING", 1).SerializeToString(),
            createWorkerStatusMessage("tcp://127.0.0.1:1", "en-GB", "WORKING", 2).SerializeToString(),
        ]
        self.run_monitor(messages)

        expected_messages = [
            {"address": "tcp://127.0.0.1:1", "model": "en-GB", "status": "WAITING", "time": 1},
            {"address": "tcp://127.0.0.1:1", "model": "en-GB", "status": "WORKING", "time": 2},
        ]

        self.assertThatMonitorForwardedMessages(expected_messages)

    def run_monitor(self, messages):
        self.socket.set_messages(messages)
        self.monitor.run()

    def assertThatMonitorForwardedMessages(self, messages):
        forwarded_messages = self.emmited_messages
        self.assertEqual(messages, forwarded_messages)

    def emit(self, message):
        self.emmited_messages.append(message)
