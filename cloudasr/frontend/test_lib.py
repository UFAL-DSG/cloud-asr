import unittest
from cloudasr.messages.helpers import *
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
        master_response = createMasterResponseMessage("SUCCESS", self.background_worker_socket)
        worker_response = createResultsMessage(True, [(1.0, "Hello World!")])

        self.master_socket = SocketSpy()
        self.master_socket.set_messages([master_response.SerializeToString()])
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
        expected_message = createWorkerRequestMessage("en-GB")
        self.assertThatMessageWasSendToMaster(expected_message)

    def test_recognize_batch_connects_to_worker(self):
        self.worker.recognize_batch(self.request_data, self.request_headers)
        self.assertThatFrontendConnectedToWorker()

    def test_recognize_batch_disconnects_from_worker_after_recognition_completion(self):
        self.worker.recognize_batch(self.request_data, self.request_headers)
        self.assertThatFrontendDisconnectedFromWorker()

    def test_recognize_batch_sends_data_to_worker(self):
        self.worker.recognize_batch(self.request_data, self.request_headers)
        expected_message = createRecognitionRequestMessage("BATCH", b"some wav", False)
        self.assertThatMessageWasSendToWorker(expected_message)

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
        response = createMasterResponseMessage("ERROR")
        self.master_socket.set_messages([response.SerializeToString()])
        self.assertRaises(NoWorkerAvailableError, lambda: self.worker.recognize_batch(self.request_data, self.request_headers))

    def test_connect_to_worker_asks_master_for_worker_address(self):
        self.worker.connect_to_worker("en-GB")
        expected_message = createWorkerRequestMessage("en-GB")
        self.assertThatMessageWasSendToMaster(expected_message)

    def test_connect_to_worker_raises_exception_when_no_worker_is_available(self):
        response = createMasterResponseMessage("ERROR")
        self.master_socket.set_messages([response.SerializeToString()])
        self.assertRaises(NoWorkerAvailableError, lambda: self.worker.connect_to_worker("en-GB"))

    def test_connect_to_worker_connects_to_worker(self):
        self.worker.connect_to_worker("en-GB")
        self.assertThatFrontendConnectedToWorker()

    def test_recognize_chunk_sends_data_to_worker(self):
        self.worker.connect_to_worker("en-GB")
        self.worker.recognize_chunk(b"some binary chunk encoded in base64", frame_rate = 44100)

        expected_message = createRecognitionRequestMessage("ONLINE", b"some binary chunk decoded from base64", True, frame_rate = 44100)
        self.assertThatMessageWasSendToWorker(expected_message)

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

        expected_message = createRecognitionRequestMessage("ONLINE", b"", False, frame_rate = 44100)
        self.assertThatMessageWasSendToWorker(expected_message)

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
        self.assertThatFrontendDisconnectedFromWorker()

    def assertThatMessageWasSendToMaster(self, message):
        sent_message = parseWorkerRequestMessage(self.master_socket.sent_message)
        self.assertEquals(message, sent_message)

    def assertThatFrontendConnectedToWorker(self):
        self.assertEquals(self.background_worker_socket, self.worker_socket.connected_to)

    def assertThatFrontendDisconnectedFromWorker(self):
        self.assertTrue(self.worker_socket.is_disconnected)

    def assertThatMessageWasSendToWorker(self, message):
        sent_message = parseRecognitionRequestMessage(self.worker_socket.sent_message)
        self.assertEquals(message, sent_message)


class DummyDecoder:

    def decode(self, data):
        return b"some binary chunk decoded from base64"
