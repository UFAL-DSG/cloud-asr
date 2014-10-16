import unittest
from lib import FrontendWorker, NoWorkerAvailableError, MissingHeaderError
from cloudasr.test_doubles import SocketSpy
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

        self.master_socket = SocketSpy()
        self.master_socket.set_messages([response.SerializeToString()])
        self.worker_socket = SocketSpy()
        self.worker_socket.set_messages([worker_response.SerializeToString()])
        self.decoder = DummyDecoder()
        self.worker = FrontendWorker(self.master_socket, self.worker_socket, self.decoder)

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
        expected_message.has_next = False

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

    def test_recognize_batch_raises_exception_when_no_worker_is_available(self):
        response = MasterResponseMessage()
        response.status = MasterResponseMessage.ERROR

        self.master_socket.set_messages([response.SerializeToString()])
        self.assertRaises(NoWorkerAvailableError, lambda: self.worker.recognize_batch(self.request_data, self.request_headers))

    def test_connect_to_worker_asks_master_for_worker_address(self):
        self.worker.connect_to_worker("en-GB")

        expected_message = WorkerRequestMessage()
        expected_message.model = "en-GB"

        received_message = WorkerRequestMessage()
        received_message.ParseFromString(self.master_socket.sent_message)

        self.assertEquals(expected_message, received_message)

    def test_connect_to_worker_raises_exception_when_no_worker_is_available(self):
        response = MasterResponseMessage()
        response.status = MasterResponseMessage.ERROR

        self.master_socket.set_messages([response.SerializeToString()])
        self.assertRaises(NoWorkerAvailableError, lambda: self.worker.connect_to_worker("en-GB"))

    def test_connect_to_worker_connects_to_worker(self):
        self.worker.connect_to_worker("en-GB")
        self.assertEquals(self.background_worker_socket, self.worker_socket.connected_to)

    def test_recognize_chunk_sends_data_to_worker(self):
        self.worker.connect_to_worker("en-GB")
        self.worker.recognize_chunk(b"some binary chunk encoded in base64", frame_rate = 44100)

        expected_message = RecognitionRequestMessage()
        expected_message.body = b"some binary chunk decoded from base64"
        expected_message.type = RecognitionRequestMessage.ONLINE
        expected_message.frame_rate = 44100
        expected_message.has_next = True

        received_message = RecognitionRequestMessage()
        received_message.ParseFromString(self.worker_socket.sent_message)

        self.assertEquals(expected_message, received_message)

    def test_recognize_chunk_reads_response_from_worker(self):
        self.worker.connect_to_worker("en-GB")
        received_response = self.worker.recognize_chunk(b"some binary chunk encoded in base64", frame_rate = 44100)

        expected_response = {
            'status': 0,
            'result': {
                'hypotheses': [
                    {'transcript': 'Hello World!'}
                ]
            },
            'final': False
        }

        self.assertEquals(expected_response, received_response)

    def test_end_recognition_sends_data_to_worker(self):
        self.worker.connect_to_worker("en-GB")
        self.worker.end_recognition()

        expected_message = RecognitionRequestMessage()
        expected_message.body = b""
        expected_message.type = RecognitionRequestMessage.ONLINE
        expected_message.frame_rate = 44100
        expected_message.has_next = False

        received_message = RecognitionRequestMessage()
        received_message.ParseFromString(self.worker_socket.sent_message)

        self.assertEquals(expected_message, received_message)

    def test_end_recognition_reads_response_from_worker(self):
        self.worker.connect_to_worker("en-GB")
        received_response = self.worker.end_recognition()

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

        self.assertEquals(expected_response, received_response)

    def test_end_recognition_disconnects_from_worker(self):
        self.worker.connect_to_worker("en-GB")
        self.worker.end_recognition()
        self.assertTrue(self.worker_socket.is_disconnected)



class DummyDecoder:

    def decode(self, data):
        return b"some binary chunk decoded from base64"
