import unittest
from types import *
from lib import Worker, ASR, AudioUtils

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

asr_response = [
    (1.0, "Hello World!")
]


class TestWorker(unittest.TestCase):

    def setUp(self):
        self.model = "en-GB"
        self.worker_address = "tcp://127.0.0.1:5678"
        self.worker_socket = SocketSpy()
        self.master_socket = MasterSocketSpy()
        self.asr = ASRSpy(asr_response)
        self.audio = DummyAudio()
        self.worker = Worker(self.model, self.worker_address, self.worker_socket, self.master_socket, self.asr, self.audio, self.worker_socket.has_next_message)

    def test_worker_forwards_wav_from_every_message_to_asr_as_pcm(self):
        self.run_worker(["message 1", "message 2"])
        self.assertEquals(["pcm message 1", "pcm message 2"], self.asr.processed_chunks)

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

    def test_asr_returns_dummy_final_hypothesis(self):
        asr = ASR()
        interim_hypothesis = asr.recognize_chunk(self.load_pcm_sample_data())
        final_hypothesis = asr.get_final_hypothesis()

        self.assertEqual(type(final_hypothesis), ListType)
        self.assertGreater(len(final_hypothesis), 0)
        for hypothesis in final_hypothesis:

            self.assertEqual(type(hypothesis[0]), FloatType)
            self.assertEqual(type(hypothesis[1]), UnicodeType)
            self.assertGreaterEqual(hypothesis[0], 0)

    def load_pcm_sample_data(self):
        audio = AudioUtils()

        return audio.load_wav_from_file_as_pcm("../resources/test.wav")


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


class DummyAudio:

    def load_wav_from_string_as_pcm(self, string):
        return "pcm " + string
