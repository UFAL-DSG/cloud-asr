import unittest
import zmq
from poller import Poller

class TestPoller(unittest.TestCase):

    def setUp(self):
        context = zmq.Context()
        worker_socket = context.socket(zmq.REP)
        worker_socket.bind("ipc:///tmp/worker")
        frontend_socket = context.socket(zmq.REP)
        frontend_socket.bind("ipc:///tmp/frontend")

        sockets = {
            "worker": {"socket": worker_socket, "receive": worker_socket.recv_json, "send": worker_socket.send_json},
            "frontend": {"socket": frontend_socket, "receive": frontend_socket.recv_json, "send": worker_socket.send_json},
        }
        time = TimeStub()

        self.poller = Poller(sockets, time)

    def test_when_nobody_sends_message_poller_returns_empty_dictionary(self):
        messages, time = self.poller.poll(timeout=1)

        self.assertEquals({}, messages)
        self.assertEquals(1, time)

    def test_when_frontend_sends_message_poller_returns_that_message(self):
        message = {"model": "en-GB"}
        self.send_message("ipc:///tmp/frontend", message)

        messages, time = self.poller.poll(timeout=1)
        self.assertReceivedMessage("frontend", message, messages)

    def test_when_worker_sends_message_poller_returns_that_message(self):
        message = {"address": "tcp://127.0.0.1:1", "model": "en-GB"}
        self.send_message("ipc:///tmp/worker", message)

        messages, time = self.poller.poll(timeout=1)
        self.assertReceivedMessage("worker", message, messages)

    def test_when_worker_and_frontend_send_message_poller_returns_both_messages(self):
        worker_message = {"address": "tcp://127.0.0.1:1", "model": "en-GB"}
        self.send_message("ipc:///tmp/worker", worker_message)

        frontend_message = {"model": "en-GB"}
        self.send_message("ipc:///tmp/frontend", frontend_message)

        messages, time = self.poller.poll(timeout=1)
        self.assertReceivedMessage("worker", worker_message, messages)
        self.assertReceivedMessage("frontend", frontend_message, messages)

    def test_when_worker_sends_two_messages_poller_should_return_both_messages_sequentially(self):
        message = {"address": "tcp://127.0.0.1:1", "model": "en-GB"}
        self.send_message("ipc:///tmp/worker", message)

        messages, time = self.poller.poll(timeout=1)
        self.poller.send("worker", {"status": "success"})
        self.assertReceivedMessage("worker", message, messages)
        self.assertEquals(1, time)

        message = {"address": "tcp://127.0.0.1:2", "model": "en-GB"}
        self.send_message("ipc:///tmp/worker", message)

        messages, time = self.poller.poll(timeout=1)
        self.poller.send("worker", {"status": "success"})
        self.assertReceivedMessage("worker", message, messages)
        self.assertEquals(2, time)

    def test_when_worker_sends_message_it_should_be_able_to_recieve_reply(self):
        message = {"address": "tcp://127.0.0.1:1", "model": "en-GB"}
        socket = self.send_message("ipc:///tmp/worker", message)

        messages, time = self.poller.poll(timeout=1)
        self.poller.send("worker", {"status": "success"})

        message = socket.recv_json()
        self.assertEquals({"status": "success"}, message)

    def assertReceivedMessage(self, name, message, messages):
        self.assertIn(name, messages)
        self.assertEquals(message, messages[name])

    def send_message(self, address, message):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(address)
        socket.send_json(message)

        return socket


class TimeStub:

    def __init__(self):
        self.time = 0

    def __call__(self):
        self.time += 1
        return self.time
