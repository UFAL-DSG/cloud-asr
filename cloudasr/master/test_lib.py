import unittest
import zmq
from lib import Master, Poller
from collections import defaultdict


class TestMaster(unittest.TestCase):

    def setUp(self):
        self.poller = PollerSpy()
        self.master = Master(self.poller, self.poller.has_next_message)

    def test_when_no_worker_is_available_master_responds_with_error(self):
        messages = [
            {"frontend": self.make_frontend_request()},
        ]
        self.run_master(messages)

        expected_message = self.make_frontend_error_response("No worker available")
        self.assertEquals([expected_message], self.poller.sent_messages["frontend"])

    def test_when_no_appropriate_worker_is_available_master_responds_with_error(self):
        messages = [
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-US")},
            {"frontend": self.make_frontend_request("en-GB")}
        ]
        self.run_master(messages)

        expected_message = self.make_frontend_error_response("No worker available")
        self.assertEquals([expected_message], self.poller.sent_messages["frontend"])

    def test_when_worker_is_available_master_sends_his_address_to_frontend(self):
        worker_address = "tcp://127.0.0.1:1"
        messages = [
            {"worker": self.make_heartbeat_request(worker_address)},
            {"frontend": self.make_frontend_request()},
            {"worker": self.make_heartbeat_request(worker_address)},
            {"frontend": self.make_frontend_request()}
        ]
        self.run_master(messages)

        expected_message = self.make_frontend_successfull_response("tcp://127.0.0.1:1")
        self.assertEquals([expected_message, expected_message], self.poller.sent_messages["frontend"])

    def test_when_worker_sends_two_heartbeats_it_is_available_only_to_first_frontend_request(self):
        worker_address = "tcp://127.0.0.1:1"
        messages = [
            {"worker": self.make_heartbeat_request(worker_address)},
            {"worker": self.make_heartbeat_request(worker_address)},
            {"frontend": self.make_frontend_request()},
            {"frontend": self.make_frontend_request()}
        ]
        self.run_master(messages)

        expected_message1 = self.make_frontend_successfull_response("tcp://127.0.0.1:1")
        expected_message2 = self.make_frontend_error_response("No worker available")
        self.assertEquals([expected_message1, expected_message2], self.poller.sent_messages["frontend"])

    def test_when_worker_sends_heartbeat_master_replies_witk_ok(self):
        worker_address = "tcp://127.0.0.1:1"
        messages = [
            {"worker": self.make_heartbeat_request(worker_address)}
        ]
        self.run_master(messages)

        expected_message = {"status": "success"}
        self.assertEquals([expected_message], self.poller.sent_messages["worker"])

    def test_when_worker_sent_heartbeat_and_went_silent_for_3600secs_then_it_is_not_available_anymore(self):
        worker_address = "tcp://127.0.0.1:1"
        messages = [
            {"worker": self.make_heartbeat_request(worker_address)},
            {"frontend": self.make_frontend_request(), "time": +3600}
        ]
        self.run_master(messages)

        expected_message = self.make_frontend_error_response("No worker available")
        self.assertEquals([expected_message], self.poller.sent_messages["frontend"])

    def run_master(self, messages):
        self.poller.add_messages(messages)
        self.master.run()

    def make_heartbeat_request(self, worker_address, model="en-GB"):
        return {
            "address": worker_address,
            "model": model
        }

    def make_frontend_request(self, model="en-GB"):
        return {
            "model": model
        }

    def make_frontend_successfull_response(self, address):
        return {
            "status": "success",
            "address": address
        }

    def make_frontend_error_response(self, message):
        return {
            "status": "error",
            "message": message
        }


class TestPoller(unittest.TestCase):

    def setUp(self):
        context = zmq.Context()
        worker_socket = context.socket(zmq.REP)
        worker_socket.bind("ipc:///tmp/worker")
        frontend_socket = context.socket(zmq.REP)
        frontend_socket.bind("ipc:///tmp/frontend")

        sockets = {
            "worker": worker_socket,
            "frontend": frontend_socket,
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


class PollerSpy:

    def __init__(self):
        self.messages = []
        self.sent_messages = defaultdict(list)
        self.time = 0

    def add_messages(self, messages):
        self.messages.extend(messages)

    def has_next_message(self):
        return len(self.messages) > 0

    def poll(self):
        messages = self.messages.pop(0)
        if "time" in messages:
            self.time += messages.pop("time")
        else:
            self.time += 1

        return messages, self.time

    def send(self, socket, message):
        self.sent_messages[socket].append(message)


class TimeStub:

    def __init__(self):
        self.time = 0

    def __call__(self):
        self.time += 1
        return self.time
