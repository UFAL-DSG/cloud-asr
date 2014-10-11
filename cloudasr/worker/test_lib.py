import unittest
import config
from types import *
from lib import Worker, Heartbeat, ASR, AudioUtils
from cloudasr.messages import HeartbeatMessage, RecognitionRequestMessage, ResultsMessage, Alternative
from cloudasr.test_doubles import PollerSpy


class TestWorker(unittest.TestCase):

    def setUp(self):
        self.model = "en-GB"
        self.worker_address = "tcp://127.0.0.1:5678"
        self.master_socket = SocketSpy()

        self.heartbeat = Heartbeat(self.model, self.worker_address, self.master_socket)
        self.poller = PollerSpy()
        self.asr = ASRSpy([(1.0, "Hello World!")], (1.0, "Interim result"))
        self.audio = DummyAudio()
        self.worker = Worker(self.poller, self.heartbeat, self.asr, self.audio, self.poller.has_next_message)

    def test_worker_forwards_wav_from_every_message_to_asr_as_pcm(self):
        messages = [
            {"frontend": self.make_fronted_request("message 1")},
            {"frontend": self.make_fronted_request("message 2")}
        ]

        self.run_worker(messages)
        self.assertEquals(["pcm message 1", "pcm message 2"], self.asr.processed_chunks)

    def test_worker_reads_final_hypothesis_from_asr(self):
        messages = [
            {"frontend": self.make_fronted_request("message 1")},
            {"frontend": self.make_fronted_request("message 2")}
        ]

        self.run_worker(messages)

        expected_message = self.make_final_results_response()
        received_messages = [self.parseResultsFromString(message) for message in self.poller.sent_messages["frontend"]]
        self.assertEquals([expected_message, expected_message], received_messages)

    def test_worker_sends_heartbeat_to_master_when_ready_to_work(self):
        messages = [{}]
        self.run_worker(messages)

        expected_message = HeartbeatMessage()
        expected_message.address = self.worker_address
        expected_message.model = self.model
        expected_message.status = HeartbeatMessage.READY

        received_messages = [self.parseHeartbeatFromString(message) for message in self.master_socket.sent_messages]
        self.assertEquals([expected_message], received_messages)

    def test_worker_sends_heartbeat_after_finishing_task(self):
        messages = [
            {"frontend": self.make_fronted_request("message 1")}
        ]
        self.run_worker(messages)

        expected_message1 = HeartbeatMessage()
        expected_message1.address = self.worker_address
        expected_message1.model = self.model
        expected_message1.status = HeartbeatMessage.READY

        expected_message2 = HeartbeatMessage()
        expected_message2.address = self.worker_address
        expected_message2.model = self.model
        expected_message2.status = HeartbeatMessage.FINISHED

        expected_messages = [expected_message1, expected_message2]
        received_messages = [self.parseHeartbeatFromString(message) for message in self.master_socket.sent_messages]

        self.assertEquals(expected_messages, received_messages)

    def test_worker_sends_interim_results_after_each_chunk(self):
        messages = [
            {"frontend": self.make_fronted_request("message 1", "online")},
            {"frontend": self.make_fronted_request("message 2", "online")}
        ]
        self.run_worker(messages)

        expected_message = self.make_interim_results_response()
        received_messages = [self.parseResultsFromString(message) for message in self.poller.sent_messages["frontend"]]
        self.assertEquals([expected_message, expected_message], received_messages)

    def test_worker_sends_final_results_after_last_chunk(self):
        messages = [
            {"frontend": self.make_fronted_request("message 1", "online", has_next = True)},
            {"frontend": self.make_fronted_request("message 2", "online", has_next = False)}
        ]
        self.run_worker(messages)

        expected_message1 = self.make_interim_results_response()
        expected_message2 = self.make_final_results_response()
        received_messages = [self.parseResultsFromString(message) for message in self.poller.sent_messages["frontend"]]

        self.assertEquals([expected_message1, expected_message2], received_messages)


    def run_worker(self, messages):
        self.poller.add_messages(messages)
        self.worker.run()

    def parseHeartbeatFromString(self, message):
        heartbeat = HeartbeatMessage()
        heartbeat.ParseFromString(message)

        return heartbeat

    def parseResultsFromString(self, message):
        result = ResultsMessage()
        result.ParseFromString(message)

        return result

    def make_fronted_request(self, message, type = "BATCH", has_next = True):
        request = RecognitionRequestMessage()
        request.type = RecognitionRequestMessage.BATCH if type == "BATCH" else RecognitionRequestMessage.ONLINE
        request.has_next = has_next
        request.body = message

        return request.SerializeToString()

    def make_interim_results_response(self):
        alternative = Alternative()
        alternative.confidence = 1.0
        alternative.transcript = "Interim result"

        interim_results = ResultsMessage()
        interim_results.final = False
        interim_results.alternatives.extend([alternative])

        return interim_results

    def make_final_results_response(self):
        alternative = Alternative()
        alternative.confidence = 1.0
        alternative.transcript = "Hello World!"

        final_results = ResultsMessage()
        final_results.final = True
        final_results.alternatives.extend([alternative])

        return final_results


class TestASR(unittest.TestCase):

    def test_asr_returns_dummy_final_hypothesis(self):
        asr = ASR(config.kaldi_config, config.wst_path)
        interim_hypothesis = asr.recognize_chunk(self.load_pcm_sample_data())
        final_hypothesis = asr.get_final_hypothesis()

        self.assertEqual(type(final_hypothesis), ListType)
        self.assertGreater(len(final_hypothesis), 0)
        for hypothesis in final_hypothesis:

            self.assertEqual(type(hypothesis[0]), FloatType)
            self.assertEqual(type(hypothesis[1]), UnicodeType)
            self.assertGreaterEqual(hypothesis[0], 0)

    def test_recognize_chunk_returns_interim_results(self):
        asr = ASR(config.kaldi_config, config.wst_path)
        interim_hypothesis = asr.recognize_chunk(self.load_pcm_sample_data())

        self.assertEquals(type(interim_hypothesis[0]), FloatType)
        self.assertEquals(type(interim_hypothesis[1]), UnicodeType)


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


class ASRSpy:

    def __init__(self, final_hypothesis, interim_hypothesis):
        self.processed_chunks = []
        self.final_hypothesis = final_hypothesis
        self.interim_hypothesis = interim_hypothesis

    def recognize_chunk(self, chunk):
        self.processed_chunks.append(chunk)

        return self.interim_hypothesis

    def get_final_hypothesis(self):
        return self.final_hypothesis


class DummyAudio:

    def load_wav_from_string_as_pcm(self, string):
        return "pcm " + string
