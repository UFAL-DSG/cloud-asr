import unittest
from lib import FrontendWorker, NoWorkerAvailableError, MissingHeaderError
from cloudasr.messages import WorkerRequestMessage, MasterResponseMessage, RecognitionRequestMessage, ResultsMessage, Alternative


class TestFrontendWorker(unittest.TestCase):

    background_worker_socket = "127.0.0.1:5678"
    request_data = {
        "model": "en-GB",
        "wav": b"some wav"
    }
    request_headers = {
        "Content-Type": "audio/x-wav; rate=44100;"
    }

    def setUp(self):
        response = MasterResponseMessage()
        response.status = MasterResponseMessage.SUCCESS
        response.address = self.background_worker_socket

        alternative = Alternative()
        alternative.confidence = 1.0
        alternative.transcript = "Hello World!"

        worker_response = ResultsMessage()
        worker_response.final = True
        worker_response.alternatives.extend([alternative])

        self.master_socket = SocketSpy(response.SerializeToString())
        self.worker_socket = SocketSpy(worker_response.SerializeToString())
        self.worker = FrontendWorker(self.master_socket, self.worker_socket)

    def test_recognize_batch_requires_content_type_header_with_frame_rate(self):
        self.assertRaises(MissingHeaderError, lambda: self.worker.recognize_batch(self.request_data,{}))
        self.assertRaises(MissingHeaderError, lambda: self.worker.recognize_batch(self.request_data,{"Content-Type":"application/x-www-form-urlencoded"}))

        self.worker.recognize_batch(self.request_data,{"Content-Type":"audio/x-wav; rate=44100;"})

    def test_recognize_batch_asks_master_for_worker_address(self):
        self.worker.recognize_batch(self.request_data, self.request_headers)

        expected_message = WorkerRequestMessage()
        expected_message.model = "en-GB"

        received_message = WorkerRequestMessage()
        received_message.ParseFromString(self.master_socket.sent_message)

        self.assertEquals(expected_message, received_message)

    def test_recognize_batch_connects_to_worker(self):
        self.worker.recognize_batch(self.request_data, self.request_headers)
        self.assertEquals(self.background_worker_socket, self.worker_socket.connected_to)

    def test_recognize_batch_disconnects_from_worker_after_recognition_completion(self):
        self.worker.recognize_batch(self.request_data, self.request_headers)
        self.assertTrue(self.worker_socket.is_disconnected)

    def test_recognize_batch_sends_data_to_worker(self):
        self.worker.recognize_batch(self.request_data, self.request_headers)

        expected_message = RecognitionRequestMessage()
        expected_message.body = b"some wav"
        expected_message.type = RecognitionRequestMessage.BATCH

        received_message = RecognitionRequestMessage()
        received_message.ParseFromString(self.worker_socket.sent_message)

        self.assertEquals(expected_message, received_message)

    def test_recognize_batch_reads_response_from_worker(self):
        expected_response = {
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

        received_response = self.worker.recognize_batch(self.request_data, self.request_headers)

        self.assertEquals(expected_response, received_response)

    def test_recognize_batch_raise_exception_when_no_worker_is_available(self):
        response = MasterResponseMessage()
        response.status = MasterResponseMessage.ERROR

        self.master_socket.set_response(response.SerializeToString())
        self.assertRaises(NoWorkerAvailableError, lambda: self.worker.recognize_batch(self.request_data, self.request_headers))


class SocketSpy:

    def __init__(self, response):
        self.response = response
        self.sent_message = None
        self.connected_to = None
        self.is_disconnected = None

    def set_response(self, response):
        self.response = response

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

    def recv(self):
        return self.response

    def recv_json(self):
        return self.response
