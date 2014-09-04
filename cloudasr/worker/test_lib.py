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
        self.received_messages = ["message 1", "message 2"]
        self.socket = socket = SocketSpy(self.received_messages[:])
        self.asr = asr = ASRSpy(dummy_final_hypothesis)
        self.worker = Worker(socket, asr, socket.has_next_message)

    def test_worker_forwards_every_message_to_asr(self):
        self.worker.run()
        print self.asr.processed_chunks
        self.assertEquals(self.received_messages, self.asr.processed_chunks)

    def test_worker_reads_final_hypothesis_from_asr(self):
        self.worker.run()
        self.assertEquals([dummy_final_hypothesis, dummy_final_hypothesis], self.socket.sent_messages)


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

    def __init__(self, messages):
        self.messages = messages
        self.sent_messages = []

    def recv(self):
        return self.messages.pop(0)

    def send_json(self, message):
        return self.sent_messages.append(message)

    def has_next_message(self):
        return len(self.messages) > 0


class ASRSpy:

    def __init__(self, final_hypothesis):
        self.processed_chunks = []
        self.final_hypothesis = final_hypothesis

    def recognize_chunk(self, chunk):
        self.processed_chunks.append(chunk)

    def get_final_hypothesis(self):
        return self.final_hypothesis
