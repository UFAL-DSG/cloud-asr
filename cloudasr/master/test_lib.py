import unittest
from lib import Master
from cloudasr.test_doubles import PollerSpy, SocketSpy
from cloudasr.messages.helpers import *


class TestMaster(unittest.TestCase):

    def setUp(self):
        self.poller = PollerSpy()
        self.monitor_socket = SocketSpy()
        self.master = Master(self.poller, self.monitor_socket, self.poller.has_next_message)

    def test_when_no_worker_is_available_master_responds_with_error(self):
        messages = [
            {"frontend": self.make_frontend_request()},
        ]

        self.run_master(messages)
        expected_message = self.make_frontend_error_response("No worker available")
        self.assertThatMessagesWereSendToFrontend([expected_message])

    def test_when_no_appropriate_worker_is_available_master_responds_with_error(self):
        messages = [
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-US", "STARTED")},
            {"frontend": self.make_frontend_request("en-GB")}
        ]

        self.run_master(messages)
        expected_message = self.make_frontend_error_response("No worker available")
        self.assertThatMessagesWereSendToFrontend([expected_message])

    def test_when_appropriate_worker_is_available_master_sends_its_address_to_client(self):
        messages = [
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "STARTED")},
            {"frontend": self.make_frontend_request()},
        ]

        self.run_master(messages)
        expected_message = self.make_frontend_successfull_response("tcp://127.0.0.1:1")
        self.assertThatMessagesWereSendToFrontend([expected_message])

    def test_worker_cant_be_assigned_to_another_client_before_finishing_its_task(self):
        messages = [
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "STARTED")},
            {"frontend": self.make_frontend_request()},
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "WORKING")},
            {"frontend": self.make_frontend_request()}
        ]

        self.run_master(messages)
        expected_message1 = self.make_frontend_successfull_response("tcp://127.0.0.1:1")
        expected_message2 = self.make_frontend_error_response("No worker available")
        self.assertThatMessagesWereSendToFrontend([expected_message1, expected_message2])

    def test_when_worker_finished_its_task_it_can_be_assigned_to_another_client(self):
        messages = [
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "STARTED")},
            {"frontend": self.make_frontend_request()},
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "FINISHED")},
            {"frontend": self.make_frontend_request()}
        ]

        self.run_master(messages)
        expected_message = self.make_frontend_successfull_response("tcp://127.0.0.1:1")
        self.assertThatMessagesWereSendToFrontend([expected_message, expected_message])

    def test_when_worker_sends_two_heartbeats_it_is_available_only_to_first_frontend_request(self):
        messages = [
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "STARTED")},
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "WAITING")},
            {"frontend": self.make_frontend_request()},
            {"frontend": self.make_frontend_request()}
        ]

        self.run_master(messages)
        expected_message1 = self.make_frontend_successfull_response("tcp://127.0.0.1:1")
        expected_message2 = self.make_frontend_error_response("No worker available")
        self.assertThatMessagesWereSendToFrontend([expected_message1, expected_message2])

    def test_when_worker_sent_heartbeat_and_went_silent_for_10secs_then_it_is_not_available_anymore(self):
        messages = [
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "STARTED")},
            {"frontend": self.make_frontend_request(), "time": +10}
        ]

        self.run_master(messages)
        expected_message = self.make_frontend_error_response("No worker available")
        self.assertThatMessagesWereSendToFrontend([expected_message])

    def test_when_worker_was_not_responding_and_then_it_sent_heartbeat_it_should_be_available_again(self):
        messages = [
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "STARTED")},
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "WAITING"), "time": +100},
            {"frontend": self.make_frontend_request()}
        ]

        self.run_master(messages)
        expected_message = self.make_frontend_successfull_response("tcp://127.0.0.1:1")
        self.assertThatMessagesWereSendToFrontend([expected_message])

    def test_when_worker_crashed_and_then_it_sent_running_heartbeat_it_should_be_available_again(self):
        messages = [
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "STARTED")},
            {"frontend": self.make_frontend_request()},
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "WORKING")},
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "STARTED")},
            {"frontend": self.make_frontend_request()}
        ]

        self.run_master(messages)
        expected_message = self.make_frontend_successfull_response("tcp://127.0.0.1:1")
        self.assertThatMessagesWereSendToFrontend([expected_message, expected_message])

    def test_when_worker_did_not_receive_first_chunk_for_10_secs_it_should_be_available_again(self):
        messages1 = [
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "STARTED")},
            {"frontend": self.make_frontend_request()}
        ]

        messages2 = [{"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "WAITING")}] * 10
        messages3 = [{"frontend": self.make_frontend_request()}]

        self.run_master(messages1 + messages2 + messages3)
        expected_message = self.make_frontend_successfull_response("tcp://127.0.0.1:1")
        self.assertThatMessagesWereSendToFrontend([expected_message, expected_message])

    def test_when_worker_sent_running_heartbeat_master_informs_monitor_that_the_worker_has_been_started(self):
        messages = [
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "STARTED")},
        ]

        self.run_master(messages)
        expected_message = self.make_worker_status_message("tcp://127.0.0.1:1", "en-GB", "STARTED", 1)
        self.assertThatMessagesWereSendToMonitor([expected_message])

    def test_when_worker_sent_ready_heartbeat_master_informs_monitor_that_the_worker_is_waiting(self):
        messages = [
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "STARTED")},
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "WAITING")},
        ]

        self.run_master(messages)
        expected_message1 = self.make_worker_status_message("tcp://127.0.0.1:1", "en-GB", "STARTED", 1)
        expected_message2 = self.make_worker_status_message("tcp://127.0.0.1:1", "en-GB", "WAITING", 2)
        self.assertThatMessagesWereSendToMonitor([expected_message1, expected_message2])

    def test_when_worker_is_assigned_to_frontend_master_informs_monitor_that_the_worker_is_working(self):
        messages = [
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "WAITING")},
            {"frontend": self.make_frontend_request()},
        ]

        self.run_master(messages)
        expected_message1 = self.make_worker_status_message("tcp://127.0.0.1:1", "en-GB", "STARTED", 1)
        expected_message2 = self.make_worker_status_message("tcp://127.0.0.1:1", "en-GB", "WORKING", 2)
        self.assertThatMessagesWereSendToMonitor([expected_message1, expected_message2])

    def test_when_worker_is_finished_master_informs_monitor_that_the_worker_is_waiting(self):
        messages = [
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "WAITING")},
            {"frontend": self.make_frontend_request()},
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-GB", "FINISHED")},
        ]

        self.run_master(messages)
        expected_message1 = self.make_worker_status_message("tcp://127.0.0.1:1", "en-GB", "STARTED", 1)
        expected_message2 = self.make_worker_status_message("tcp://127.0.0.1:1", "en-GB", "WORKING", 2)
        expected_message3 = self.make_worker_status_message("tcp://127.0.0.1:1", "en-GB", "WAITING", 3)
        self.assertThatMessagesWereSendToMonitor([expected_message1, expected_message2, expected_message3])

    def run_master(self, messages):
        self.poller.add_messages(messages)
        self.master.run()

    def assertThatMessagesWereSendToFrontend(self, messages):
        sent_messages = [parseMasterResponseMessage(message) for message in self.poller.sent_messages["frontend"]]
        self.assertEquals(messages, sent_messages)

    def assertThatMessagesWereSendToMonitor(self, messages):
        sent_messages = [parseWorkerStatusMessage(message) for message in self.monitor_socket.sent_messages]
        self.assertEquals(messages, sent_messages)

    def make_heartbeat_request(self, worker_address, model, status):
        return createHeartbeatMessage(worker_address, model, status).SerializeToString()

    def make_frontend_request(self, model="en-GB"):
        return createWorkerRequestMessage(model).SerializeToString()

    def make_frontend_successfull_response(self, address):
        return createMasterResponseMessage("SUCCESS", address)

    def make_frontend_error_response(self, message):
        return createMasterResponseMessage("ERROR")

    def make_worker_status_message(self, address, model, status, time):
        return createWorkerStatusMessage(address, model, status, time)
