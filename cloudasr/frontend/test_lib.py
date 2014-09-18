import unittest
from lib import FrontendWorker


class TestFrontendWorker(unittest.TestCase):

    background_worker_socket = "127.0.0.1:5678"
    request_data = {
        "model": "en-GB",
        "wav": b"some wav"
    }
    dummy_response = {
        "result": [
            {
                "alternative": [
                    {
                        "confidence": 1.0,
                        "transcript": "Hello World!"
                    },
                ],
                "final": True,
            },
        ],
        "result_index": 0,
    }

    def setUp(self):
        self.master_socket = SocketSpy({"status": "success", "address": self.background_worker_socket})
        self.worker_socket = SocketSpy(self.dummy_response)
        self.worker = FrontendWorker(self.master_socket, self.worker_socket)

    def test_recognize_batch_asks_master_for_worker_address(self):
        self.worker.recognize_batch(self.request_data)
        self.assertEquals({"model": "en-GB"}, self.master_socket.sent_message)

    def test_recognize_batch_connects_to_worker(self):
        self.worker.recognize_batch(self.request_data)
        self.assertEquals(self.background_worker_socket, self.worker_socket.connected_to)

    def test_recognize_batch_disconnects_from_worker_after_recognition_completion(self):
        self.worker.recognize_batch(self.request_data)
        self.assertTrue(self.worker_socket.is_disconnected)

    def test_recognize_batch_sends_data_to_worker(self):
        self.worker.recognize_batch(self.request_data)
        self.assertEquals(b"some wav", self.worker_socket.sent_message)

    def test_recognize_batch_reads_response_from_worker(self):
        response = self.worker.recognize_batch(self.request_data)
        self.assertEquals(self.dummy_response, response)


class SocketSpy:

    def __init__(self, response):
        self.response = response
        self.sent_message = None
        self.connected_to = None
        self.is_disconnected = None

    def connect(self, address):
        self.connected_to = address
        self.is_disconnected = False

    def disconnect(self, address):
        if address == self.connected_to:
            self.is_disconnected = True

    def send(self, message):
        self.sent_message = message

    def send_json(self, message):
        self.sent_message = message

    def recv_json(self):
        return self.response
