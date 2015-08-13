import unittest
from lib import Monitor
from cloudasr.test_doubles import PollerSpy
from cloudasr.messages.helpers import *


class TestMonitor(unittest.TestCase):

    def setUp(self):
        self.poller = PollerSpy()
        self.scale_workers = ScaleWorkersSpy()
        self.create_poller = lambda: self.poller
        self.monitor = Monitor(self.create_poller, self.emit, self.scale_workers, self.poller.has_next_message)
        self.emmited_messages = []

    def test_monitor_forwards_messages_to_socketio(self):
        messages = [
            createWorkerStatusMessage("tcp://127.0.0.1:1", "en-GB", "STARTED", 1).SerializeToString(),
            createWorkerStatusMessage("tcp://127.0.0.1:1", "en-GB", "WORKING", 2).SerializeToString(),
        ]
        self.run_monitor(messages)

        expected_messages = [
            {"address": "tcp://127.0.0.1:1", "model": "en-GB", "status": "STARTED", "time": 1},
            {"address": "tcp://127.0.0.1:1", "model": "en-GB", "status": "WORKING", "time": 2},
        ]

        self.assertThatMonitorForwardedMessages(expected_messages)

    def test_monitor_saves_worker_statuses(self):
        messages = [
            createWorkerStatusMessage("tcp://127.0.0.1:1", "en-GB", "STARTED", 1).SerializeToString(),
            createWorkerStatusMessage("tcp://127.0.0.1:2", "en-GB", "WORKING", 2).SerializeToString(),
        ]
        self.run_monitor(messages)

        expected_messages = [
            {"address": "tcp://127.0.0.1:1", "model": "en-GB", "status": "STARTED", "time": 1},
            {"address": "tcp://127.0.0.1:2", "model": "en-GB", "status": "WORKING", "time": 2},
        ]

        self.assertEqual(expected_messages, self.monitor.get_statuses())

    def test_monitor_will_add_new_workers_when_all_workers_are_working(self):
        messages = [
            createWorkerStatusMessage("tcp://127.0.0.1:1", "en-GB", "WORKING", 1).SerializeToString()
        ]
        self.run_monitor(messages)

        expected_messages = [
            {"en-GB": +1}
        ]
        self.assertEqual(expected_messages, self.scale_workers.scaling_history)

    def test_monitor_will_not_add_new_workers_when_it_is_currently_adding_new_workers(self):
        messages = [
            createWorkerStatusMessage("tcp://127.0.0.1:1", "en-GB", "WORKING", 1).SerializeToString(),
            createWorkerStatusMessage("tcp://127.0.0.1:1", "en-GB", "WORKING", 2).SerializeToString()
        ]
        self.run_monitor(messages)

        expected_messages = [{"en-GB": +1}, {}]
        self.assertEqual(expected_messages, self.scale_workers.scaling_history)

    def test_monitor_will_add_new_workers_when_it_finished_scaling_and_it_needs_new_workers(self):
        messages = [
            createWorkerStatusMessage("tcp://127.0.0.1:1", "en-GB", "WORKING", 1).SerializeToString(),
            createWorkerStatusMessage("tcp://127.0.0.1:1", "en-GB", "WORKING", 2).SerializeToString(),
            createWorkerStatusMessage("tcp://127.0.0.1:2", "en-GB", "STARTED", 3).SerializeToString(),
            createWorkerStatusMessage("tcp://127.0.0.1:1", "en-GB", "WORKING", 4).SerializeToString(),
            createWorkerStatusMessage("tcp://127.0.0.1:2", "en-GB", "WORKING", 5).SerializeToString()
        ]
        self.run_monitor(messages)

        expected_messages = [{"en-GB": +1}, {}, {}, {}, {"en-GB": +1}]
        self.assertEqual(expected_messages, self.scale_workers.scaling_history)


    def run_monitor(self, messages):
        self.poller.add_messages([{"master": message} for message in messages])
        self.monitor.run()

    def assertThatMonitorForwardedMessages(self, messages):
        forwarded_messages = self.emmited_messages
        self.assertEqual(messages, forwarded_messages)

    def emit(self, message):
        self.emmited_messages.append(message)


class ScaleWorkersSpy:

    def __init__(self):
        self.scaling_history = []

    def __call__(self, commands):
        self.scaling_history.append(commands)
