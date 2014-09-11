import unittest
from lib import Worker, ASR

dummy_final_hypothesis = {
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


class TestWorker(unittest.TestCase):

    def setUp(self):
        self.model = "en-GB"
        self.worker_address = "tcp://127.0.0.1:5678"
        self.worker_socket = SocketSpy()
        self.master_socket = MasterSocketSpy()
        self.asr = ASRSpy(dummy_final_hypothesis)
        self.worker = Worker(self.model, self.worker_address, self.worker_socket, self.master_socket, self.asr, self.worker_socket.has_next_message)

    def test_worker_forwards_every_message_to_asr(self):
        self.run_worker(["message 1", "message 2"])
        self.assertEquals(["message 1", "message 2"], self.asr.processed_chunks)

    def test_worker_reads_final_hypothesis_from_asr(self):
        self.run_worker(["message 1", "message 2"])
        self.assertEquals([dummy_final_hypothesis, dummy_final_hypothesis], self.worker_socket.sent_messages)

    def test_worker_sends_heartbeat_to_master_when_ready_to_work(self):
        self.run_worker(["message 1", "message 2"])

        expected_message = {
            "address": self.worker_address,
            "model": self.model
        }

        self.assertEquals([expected_message, expected_message], self.master_socket.sent_messages)

    def run_worker(self, messages):
        self.worker_socket.add_messages(messages)
        self.worker.run()


class TestASR(unittest.TestCase):

    def test_can_create_instance(self):
        asr = ASR()

    def test_asr_can_recognize_chunk(self):
        asr = ASR()
        asr.recognize_chunk(b"chunk")

    def test_asr_returns_dummy_final_hypothesis(self):
        asr = ASR()
        asr.recognize_chunk(b"chunk")
        final_hypothesis = asr.get_final_hypothesis()

        self.assertEquals(dummy_final_hypothesis, final_hypothesis)


class SocketSpy:

    def __init__(self):
        self.messages = []
        self.sent_messages = []

    def add_messages(self, messages):
        self.messages.extend(messages)

    def recv(self):
        return self.messages.pop(0)

    def send(self, message):
        return self.sent_messages.append(message)

    def send_json(self, message):
        return self.sent_messages.append(message)

    def has_next_message(self):
        return len(self.messages) > 0

class MasterSocketSpy(SocketSpy):

    def recv(self):
        return "OK"


class ASRSpy:

    def __init__(self, final_hypothesis):
        self.processed_chunks = []
        self.final_hypothesis = final_hypothesis

    def recognize_chunk(self, chunk):
        self.processed_chunks.append(chunk)

    def get_final_hypothesis(self):
        return self.final_hypothesis
