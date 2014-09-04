import unittest
from lib import FrontendWorker


class TestFrontendWorker(unittest.TestCase):

    background_worker_socket = "127.0.0.1:5678"
    request_data = b"some request data"
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
        self.socket = SocketSpy(self.dummy_response)
        self.worker = FrontendWorker(self.socket)

    def test_recognize_batch_sends_data_to_worker(self):
        self.worker.recognize_batch(self.request_data)
        self.assertEquals(self.request_data, self.socket.sent_message)

    def test_recognize_batch_reads_response_from_worker(self):
        response = self.worker.recognize_batch(self.request_data)
        self.assertEquals(self.dummy_response, response)


class SocketSpy:

    def __init__(self, response):
        self.response = response
        self.sent_message = None

    def send(self, message):
        self.sent_message = message

    def recv_json(self):
        return self.response
