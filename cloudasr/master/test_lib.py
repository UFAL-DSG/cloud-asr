import unittest
from lib import Master
from cloudasr.test_doubles import PollerSpy
from cloudasr.messages import HeartbeatMessage


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
            {"worker": self.make_heartbeat_request("tcp://127.0.0.1:1", "en-US", "READY")},
            {"frontend": self.make_frontend_request("en-GB")}
        ]
        self.run_master(messages)

        expected_message = self.make_frontend_error_response("No worker available")
        self.assertEquals([expected_message], self.poller.sent_messages["frontend"])

    def test_when_appropriate_worker_is_available_master_sends_its_address_to_client(self):
        worker_address = "tcp://127.0.0.1:1"
        messages = [
            {"worker": self.make_heartbeat_request(worker_address, "en-GB", "READY")},
            {"frontend": self.make_frontend_request()},
        ]
        self.run_master(messages)

        expected_message = self.make_frontend_successfull_response("tcp://127.0.0.1:1")
        self.assertEquals([expected_message], self.poller.sent_messages["frontend"])

    def test_worker_cant_be_assigned_to_another_client_before_finishing_its_task(self):
        worker_address = "tcp://127.0.0.1:1"
        messages = [
            {"worker": self.make_heartbeat_request(worker_address, "en-GB", "READY")},
            {"frontend": self.make_frontend_request()},
            {"worker": self.make_heartbeat_request(worker_address, "en-GB", "READY")},
            {"frontend": self.make_frontend_request()}
        ]
        self.run_master(messages)

        expected_message1 = self.make_frontend_successfull_response("tcp://127.0.0.1:1")
        expected_message2 = self.make_frontend_error_response("No worker available")
        self.assertEquals([expected_message1, expected_message2], self.poller.sent_messages["frontend"])

    def test_when_worker_finished_its_task_it_can_be_assigned_to_another_client(self):
        worker_address = "tcp://127.0.0.1:1"
        messages = [
            {"worker": self.make_heartbeat_request(worker_address, "en-GB", "READY")},
            {"frontend": self.make_frontend_request()},
            {"worker": self.make_heartbeat_request(worker_address, "en-GB", "FINISHED")},
            {"worker": self.make_heartbeat_request(worker_address, "en-GB", "READY")},
            {"frontend": self.make_frontend_request()}
        ]
        self.run_master(messages)

        expected_message = self.make_frontend_successfull_response("tcp://127.0.0.1:1")
        self.assertEquals([expected_message, expected_message], self.poller.sent_messages["frontend"])

    def test_when_worker_sends_two_heartbeats_it_is_available_only_to_first_frontend_request(self):
        worker_address = "tcp://127.0.0.1:1"
        messages = [
            {"worker": self.make_heartbeat_request(worker_address, "en-GB", "READY")},
            {"worker": self.make_heartbeat_request(worker_address, "en-GB", "READY")},
            {"frontend": self.make_frontend_request()},
            {"frontend": self.make_frontend_request()}
        ]
        self.run_master(messages)

        expected_message1 = self.make_frontend_successfull_response("tcp://127.0.0.1:1")
        expected_message2 = self.make_frontend_error_response("No worker available")
        self.assertEquals([expected_message1, expected_message2], self.poller.sent_messages["frontend"])

    def test_when_worker_sent_heartbeat_and_went_silent_for_10secs_then_it_is_not_available_anymore(self):
        worker_address = "tcp://127.0.0.1:1"
        messages = [
            {"worker": self.make_heartbeat_request(worker_address, "en-GB", "READY")},
            {"frontend": self.make_frontend_request(), "time": +10}
        ]
        self.run_master(messages)

        expected_message = self.make_frontend_error_response("No worker available")
        self.assertEquals([expected_message], self.poller.sent_messages["frontend"])

    def test_when_worker_was_not_responding_and_then_it_sent_heartbeat_it_should_be_available_again(self):
        worker_address = "tcp://127.0.0.1:1"
        messages = [
            {"worker": self.make_heartbeat_request(worker_address, "en-GB", "READY")},
            {"worker": self.make_heartbeat_request(worker_address, "en-GB", "READY"), "time": +100},
            {"frontend": self.make_frontend_request()}
        ]
        self.run_master(messages)

        expected_message = self.make_frontend_successfull_response("tcp://127.0.0.1:1")
        self.assertEquals([expected_message], self.poller.sent_messages["frontend"])

    def run_master(self, messages):
        self.poller.add_messages(messages)
        self.master.run()

    def make_heartbeat_request(self, worker_address, model, status):
        message = HeartbeatMessage()
        message.address = worker_address
        message.model = model

        if status == "READY":
            message.status = HeartbeatMessage.READY

        if status == "FINISHED":
            message.status = HeartbeatMessage.FINISHED

        return message.SerializeToString()

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
