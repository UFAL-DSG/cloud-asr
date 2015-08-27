import unittest
import config
from lib import Worker, Heartbeat, RemoteSaver
from cloudasr.messages.helpers import *
from cloudasr.test_doubles import PollerSpy, SocketSpy


class TestWorker(unittest.TestCase):

    def setUp(self):
        self.model = "en-GB"
        self.worker_address = "tcp://127.0.0.1:5678"
        self.master_socket = SocketSpy()
        self.saver = SaverSpy()
        self.vad = VADDummy()
        self.id_generator = IDGeneratorDummy()

        self.heartbeat = Heartbeat(self.model, self.worker_address, self.master_socket)
        self.poller = PollerSpy()
        self.asr = ASRSpy([(1.0, "Hello World!")], (1.0, "Interim result"))
        self.audio = DummyAudio()
        self.worker = Worker(self.poller, self.heartbeat, self.asr, self.audio, self.saver, self.vad, self.id_generator, self.poller.has_next_message)

    def test_worker_forwards_resampled_wav_from_every_message_to_asr_as_pcm(self):
        messages = [
            {"frontend": self.make_frontend_request("message 1")},
            {"frontend": self.make_frontend_request("message 2")}
        ]

        self.run_worker(messages)
        self.assertThatAsrProcessedChunks(["resampled pcm message 1", "resampled pcm message 2"])

    def test_worker_reads_final_hypothesis_from_asr(self):
        messages = [
            {"frontend": self.make_frontend_request("message 1")},
            {"frontend": self.make_frontend_request("message 2")}
        ]

        self.run_worker(messages)
        expected_message = createResultsMessage([(0, True, [(1.0, "Hello World!")])])
        self.assertThatMessagesWereSendToFrontend([expected_message, expected_message])

    def test_worker_sends_interim_results_after_each_chunk(self):
        messages = [
            {"frontend": self.make_frontend_request("message 1", "ONLINE")},
            {"frontend": self.make_frontend_request("message 2", "ONLINE")}
        ]

        self.run_worker(messages)
        expected_message = createResultsMessage([(0, False, [(1.0, "Interim result")])])
        self.assertThatMessagesWereSendToFrontend([expected_message, expected_message])

    def test_worker_sends_final_results_after_last_chunk(self):
        messages = [
            {"frontend": self.make_frontend_request("message 1", "ONLINE", has_next = True)},
            {"frontend": self.make_frontend_request("message 2", "ONLINE", has_next = False)}
        ]

        self.run_worker(messages)
        expected_message1 = createResultsMessage([(0, False, [(1.0, "Interim result")])])
        expected_message2 = createResultsMessage([(0, True, [(1.0, "Hello World!")])])
        self.assertThatMessagesWereSendToFrontend([expected_message1, expected_message2])

    def test_when_worker_receives_chunk_with_bad_id_it_should_return_error_message(self):
        messages = [
            {"frontend": self.make_frontend_request("message 1", "ONLINE", has_next = True, id = 1)},
            {"frontend": self.make_frontend_request("message 2", "ONLINE", has_next = True, id = 2)},
            {"frontend": self.make_frontend_request("message 1", "ONLINE", has_next = False, id = 1)},
        ]

        self.run_worker(messages)
        expected_message1 = createResultsMessage([(0, False, [(1.0, "Interim result")])])
        expected_message2 = createErrorResultsMessage()
        expected_message3 = createResultsMessage([(0, True, [(1.0, "Hello World!")])])
        self.assertThatMessagesWereSendToFrontend([expected_message1, expected_message2, expected_message3])

    def test_worker_forwards_resampled_pcm_chunks_from_every_message_to_asr(self):
        messages = [
            {"frontend": self.make_frontend_request("message 1", "ONLINE", has_next = True)},
            {"frontend": self.make_frontend_request("message 2", "ONLINE", has_next = True)}
        ]

        self.run_worker(messages)
        self.assertThatAsrProcessedChunks(["resampled message 1", "resampled message 2"])

    def test_worker_sends_heartbeat_to_master_when_ready_to_work(self):
        messages = []
        self.run_worker(messages)
        self.assertThatHeartbeatsWereSent(["STARTED"])

    def test_worker_sends_heartbeat_after_finishing_task(self):
        messages = [
            {"frontend": self.make_frontend_request("message 1")}
        ]

        self.run_worker(messages)
        self.assertThatHeartbeatsWereSent(["STARTED", "FINISHED"])

    def test_worker_sends_working_heartbeats_during_online_recognition(self):
        messages = [
            {"frontend": self.make_frontend_request("message 1", "ONLINE", has_next = True)},
            {"frontend": self.make_frontend_request("message 2", "ONLINE", has_next = True)},
            {"frontend": self.make_frontend_request("message 2", "ONLINE", has_next = False)}
        ]

        self.run_worker(messages)
        self.assertThatHeartbeatsWereSent(["STARTED", "WORKING", "WORKING", "FINISHED"])

    def test_worker_sends_finished_heartbeat_after_end_of_online_recognition(self):
        messages = [
            {"frontend": self.make_frontend_request("message 1", "ONLINE", has_next = True)},
            {"frontend": self.make_frontend_request("message 2", "ONLINE", has_next = False)}
        ]

        self.run_worker(messages)
        self.assertThatHeartbeatsWereSent(["STARTED", "WORKING", "FINISHED"])

    def test_worker_sends_finished_heartbeat_when_it_doesnt_receive_any_chunk_for_1sec(self):
        messages = [
            {"frontend": self.make_frontend_request("message 1", "ONLINE", has_next = True)},
            {"time": +1}
        ]

        self.run_worker(messages)
        self.assertThatHeartbeatsWereSent(["STARTED", "WORKING", "FINISHED"])

    def test_worker_sends_resets_asr_engine_when_it_doesnt_receive_any_chunk_for_1sec(self):
        messages = [
            {"frontend": self.make_frontend_request("message 1", "ONLINE", has_next = True)},
            {"time": +1}
        ]

        self.run_worker(messages)
        self.assertTrue(self.asr.resetted)

    def test_worker_sends_ready_heartbeat_when_it_doesnt_receive_any_task(self):
        messages = [{}]
        self.run_worker(messages)
        self.assertThatHeartbeatsWereSent(["STARTED", "WAITING"])

    def test_worker_saves_pcm_data_from_batch_request(self):
        messages = [
            {"frontend": self.make_frontend_request("message", "BATCH", id = 1, has_next = False)},
        ]

        self.run_worker(messages)
        self.assertThatDataWasStored({
            1: {"frame_rate": 16000, "chunks": [{"chunk_id": 0, "pcm": "pcm message", "hypothesis": [(1.0, "Hello World!")]}]}
        })

    def test_worker_saves_pcm_data_from_online_request_in_original_frame_rate(self):
        messages = [
            {"frontend": self.make_frontend_request("message 1", "ONLINE", id = 1, has_next = True)},
            {"frontend": self.make_frontend_request("message 2", "ONLINE", id = 1, has_next = True)},
            {"frontend": self.make_frontend_request("message 3", "ONLINE", id = 1, has_next = False)},
        ]

        self.run_worker(messages)
        self.assertThatDataWasStored({
            1: {"frame_rate": 44100, "chunks": [{"chunk_id": 0, "pcm": "message 1message 2message 3", "hypothesis": [(1.0, "Hello World!")]}]}
        })

    def test_worker_forwards_pcm_data_to_vad(self):
        messages = [
            {"frontend": self.make_frontend_request("message 1", "ONLINE", id = 1, has_next = False)}
        ]

        self.run_worker(messages)
        self.assertThatVadReceivedChunks([("message 1", "resampled message 1")])

    def test_worker_sends_empty_hypothesis_when_vad_detects_silence(self):
        self.vad.set_messages([
            (False, None, "", ""),
            (False, None, "", ""),
        ])

        messages = [
            {"frontend": self.make_frontend_request("silence 1", "ONLINE", id = 1, has_next = True)},
            {"frontend": self.make_frontend_request("silence 2", "ONLINE", id = 1, has_next = True)},
        ]

        self.run_worker(messages)

        expected_message = createResultsMessage([(0, False, [(1.0, "")])])
        self.assertThatMessagesWereSendToFrontend([expected_message, expected_message])

    def test_worker_sends_hypothesis_when_vad_detects_speech(self):
        self.vad.set_messages([
            (True, None, "message 1", "resampled message 1"),
            (True, None, "message 2", "resampled message 2")
        ])

        messages = [
            {"frontend": self.make_frontend_request("speech 1", "ONLINE", id = 1, has_next = True)},
            {"frontend": self.make_frontend_request("speech 2", "ONLINE", id = 1, has_next = True)},
        ]

        self.run_worker(messages)

        expected_message = createResultsMessage([(0, False, [(1.0, "Interim result")])])
        self.assertThatMessagesWereSendToFrontend([expected_message, expected_message])

    def test_worker_sends_final_hypothesis_when_vad_detects_change_to_silence(self):
        self.vad.set_messages([
            (True, None, "speech 1", "resampled speech 1"),
            (False, "non-speech", "", "")
        ])

        messages = [
            {"frontend": self.make_frontend_request("speech 1", "ONLINE", id = 1, has_next = True)},
            {"frontend": self.make_frontend_request("silence 1", "ONLINE", id = 1, has_next = True)},
        ]

        self.run_worker(messages)

        expected_message1 = createResultsMessage([(0, False, [(1.0, "Interim result")])])
        expected_message2 = createResultsMessage([(0, True, [(1.0, "Hello World!")])])
        self.assertThatMessagesWereSendToFrontend([expected_message1, expected_message2])

    def test_worker_sends_working_heartbeat_when_vad_detects_change_to_silence(self):
        self.vad.set_messages([
            (True, None, "speech 1", "resampled speech 1"),
            (False, "non-speech", "", "")
        ])

        messages = [
            {"frontend": self.make_frontend_request("speech 1", "ONLINE", id = 1, has_next = True)},
            {"frontend": self.make_frontend_request("silence 1", "ONLINE", id = 1, has_next = True)},
        ]

        self.run_worker(messages)
        self.assertThatHeartbeatsWereSent(["STARTED", "WORKING", "WORKING"])

    def test_worker_resets_asr_when_vad_detects_change_to_silence(self):
        self.vad.set_messages([
            (True, None, "speech 1", "resampled speech 1"),
            (False, "non-speech", "", "")
        ])

        messages = [
            {"frontend": self.make_frontend_request("speech 1", "ONLINE", id = 1, has_next = True)},
            {"frontend": self.make_frontend_request("silence 1", "ONLINE", id = 1, has_next = True)},
        ]

        self.run_worker(messages)
        self.assertTrue(self.asr.resetted)


    def test_worker_saves_pcm_as_part_of_original_request(self):
        self.vad.set_messages([
            (True, None, "speech 1", "resampled speech 1"),
            (False, "non-speech", "", ""),
            (True, None, "speech 2", "resampled speech 2"),
            (False, "non-speech", "", "")
        ])

        messages = [
            {"frontend": self.make_frontend_request("speech 1", "ONLINE", id = 1, has_next = True)},
            {"frontend": self.make_frontend_request("silence 1", "ONLINE", id = 1, has_next = True)},
            {"frontend": self.make_frontend_request("speech 2", "ONLINE", id = 1, has_next = True)},
            {"frontend": self.make_frontend_request("silence 2", "ONLINE", id = 1, has_next = True)},
        ]

        self.run_worker(messages)
        self.assertThatDataWasStored({
            1: {"frame_rate": 44100, "chunks": [
                {"chunk_id": 0, "pcm": "speech 1", "hypothesis": [(1.0, "Hello World!")]},
                {"chunk_id": 0, "pcm": "speech 2", "hypothesis": [(1.0, "Hello World!")]}
            ]}
        })

    def test_worker_sends_interim_result_for_last_speech_in_splitted_chunks(self):
        self.audio.set_chunks(["chunk 1", "chunk 2"])

        self.vad.set_messages([
            (True, None, "chunk 1", "resampled chunk 1"),
            (True, None, "chunk 2", "resampled chunk 2"),
        ])

        messages = [
            {"frontend": self.make_frontend_request("speech 1", "ONLINE", id = 1, has_next = True)},
        ]

        self.run_worker(messages)
        expected_messages = createResultsMessage([(0, False, [(1.0, "Interim result")])])
        self.assertThatMessagesWereSendToFrontend([expected_messages])

    def test_worker_sends_final_results_for_each_speech_in_splitted_chunks(self):
        self.audio.set_chunks(["chunk 1", "chunk 2", "chunk 3", "chunk 4"])
        self.vad.set_messages([
            (True, None, "chunk 1", "resampled chunk 1"),
            (False, "non-speech", "", ""),
            (True, None, "chunk 2", "resampled chunk 2"),
            (False, "non-speech", "", ""),
        ])

        messages = [
            {"frontend": self.make_frontend_request("speech 1", "ONLINE", id = 1, has_next = True)},
        ]

        self.run_worker(messages)
        expected_messages = createResultsMessage([(0, True, [(1.0, "Hello World!")])] * 2)
        self.assertThatMessagesWereSendToFrontend([expected_messages])

    def test_worker_sends_buffered_chunks_to_saver_when_speech_is_detected(self):
        self.vad.set_messages([
            (True, "speech", "buffered chunk", "resampled buffered chunk"),
            (False, "non-speech", "", "")
        ])

        messages = [
            {"frontend": self.make_frontend_request("speech 1", "ONLINE", id = 1, has_next = True)},
            {"frontend": self.make_frontend_request("speech 2", "ONLINE", id = 1, has_next = True)},
        ]

        self.run_worker(messages)
        self.assertThatDataWasStored({
            1: {"frame_rate": 44100, "chunks": [
                {"chunk_id": 0, "pcm": "buffered chunk", "hypothesis": [(1.0, "Hello World!")]},
            ]}
        })

    def test_worker_resets_vad_at_the_end_of_recognition(self):
        messages = [
            {"frontend": self.make_frontend_request("message 1", "ONLINE", has_next = False)}
        ]

        self.run_worker(messages)
        self.assertTrue(self.vad.resetted)

    def test_worker_resets_audio_utls_at_the_end_of_online_recognition(self):
        messages = [
            {"frontend": self.make_frontend_request("message 1", "ONLINE", has_next = False)}
        ]

        self.run_worker(messages)
        self.assertTrue(self.audio.resetted)

    def test_worker_change_lm_when_new_lm_is_set(self):
        messages = [
            {"frontend": self.make_frontend_request("", "ONLINE", new_lm = "new_lm")}
        ]

        self.run_worker(messages)
        self.assertEquals("new_lm", self.asr.lm)

    def test_worker_sends_final_result_when_lm_is_changed(self):
        self.audio.set_chunks([])
        messages = [
            {"frontend": self.make_frontend_request("", "ONLINE", new_lm = "new_lm")}
        ]

        self.run_worker(messages)
        expected_messages = createResultsMessage([(0, True, [(1.0, "Hello World!")])])
        self.assertThatMessagesWereSendToFrontend([expected_messages])

    def test_worker_sets_lm_to_default_at_the_end_of_recognition(self):
        messages = [
            {"frontend": self.make_frontend_request("", "ONLINE", has_next = False)}
        ]

        self.run_worker(messages)
        self.assertEquals("default", self.asr.lm)

    def test_worker_assings_unique_id_to_each_chunk(self):
        self.id_generator.set_ids([0,1])
        self.audio.set_chunks(["chunk 1", "chunk 2", "chunk 3", "chunk 4"])
        self.vad.set_messages([
            (True, None, "chunk 1", "resampled chunk 1"),
            (False, "non-speech", "", ""),
            (True, None, "chunk 2", "resampled chunk 2"),
            (False, "non-speech", "", ""),
        ])

        messages = [
            {"frontend": self.make_frontend_request("speech 1", "ONLINE", id = 1, has_next = True)},
        ]

        self.run_worker(messages)
        expected_messages = createResultsMessage([(0, True, [(1.0, "Hello World!")]), (1, True, [(1.0, "Hello World!")])])
        self.assertThatMessagesWereSendToFrontend([expected_messages])

    def test_worker_assings_unique_id_to_each_batch_request(self):
        self.id_generator.set_ids([0,1])
        messages = [
            {"frontend": self.make_frontend_request("speech 1", "BATCH", id = 1, has_next = False)},
            {"frontend": self.make_frontend_request("speech 2", "BATCH", id = 1, has_next = False)},
        ]

        self.run_worker(messages)
        expected_message1 = createResultsMessage([(0, True, [(1.0, "Hello World!")])])
        expected_message2 = createResultsMessage([(1, True, [(1.0, "Hello World!")])])
        self.assertThatMessagesWereSendToFrontend([expected_message1, expected_message2])

    def run_worker(self, messages):
        self.poller.add_messages(messages)
        self.worker.run()

    def assertThatAsrProcessedChunks(self, chunks):
        self.assertEquals(chunks, self.asr.processed_chunks)

    def assertThatMessagesWereSendToFrontend(self, messages):
        sent_messages = [parseResultsMessage(message) for message in self.poller.sent_messages["frontend"]]
        self.assertEquals(messages, sent_messages)

    def assertThatHeartbeatsWereSent(self, heartbeats):
        heartbeats = [self.make_heartbeat(state) for state in heartbeats]
        sent_heartbeats = [parseHeartbeatMessage(message) for message in self.master_socket.sent_messages]

        self.assertEquals(heartbeats, sent_heartbeats)

    def assertThatDataWasStored(self, data):
        self.assertEquals(data, self.saver.saved_data)

    def assertThatVadReceivedChunks(self, data):
        self.assertEquals(data, self.vad.data)

    def make_frontend_request(self, message, type = "BATCH", has_next = True, id = 0, new_lm = ""):
        return createRecognitionRequestMessage(type, message, has_next, id, 44100, new_lm).SerializeToString()

    def make_heartbeat(self, status):
        return createHeartbeatMessage(self.worker_address, self.model, status)


class RemoteSaverTest(unittest.TestCase):

    def setUp(self):
        self.id = 0
        self.chunk_id = 0
        self.part = 0
        self.final_hypothesis = [(1.0, "Hello World!")]
        self.model = "en-GB"
        self.chunk = b"chunk"
        self.frame_rate = 44100
        self.socket = SocketSpy()
        self.saver = RemoteSaver(self.socket, self.model)

    def test_saver_sends_all_information(self):
        self.saver.new_recognition(createUniqueID(self.id), self.frame_rate)
        self.saver.add_pcm(self.chunk)
        self.saver.add_pcm(self.chunk)
        self.saver.final_hypothesis(self.chunk_id, self.final_hypothesis)

        message = parseSaverMessage(self.socket.sent_message)
        self.assertEquals(self.id, uniqId2Int(message.id))
        self.assertEquals(self.part, message.part)
        self.assertEquals(self.model, message.model)
        self.assertEquals(self.chunk * 2, message.body)
        self.assertEquals(self.frame_rate, message.frame_rate)
        self.assertEquals([{"confidence": self.final_hypothesis[0][0], "transcript": self.final_hypothesis[0][1]}], alternatives2List(message.alternatives))

    def test_saver_sends_all_parts(self):
        self.saver.new_recognition(createUniqueID(self.id), self.frame_rate)
        self.saver.add_pcm(self.chunk)
        self.saver.final_hypothesis(self.chunk_id, self.final_hypothesis)
        self.saver.add_pcm(self.chunk)
        self.saver.final_hypothesis(self.chunk_id, self.final_hypothesis)

        message = parseSaverMessage(self.socket.sent_messages[0])
        self.assertEquals(0, message.part)

        message = parseSaverMessage(self.socket.sent_messages[1])
        self.assertEquals(1, message.part)

    def test_saver_resets_after_final_hypothesis(self):
        self.saver.new_recognition(createUniqueID(self.id))
        self.saver.add_pcm(self.chunk)
        self.saver.final_hypothesis(self.chunk_id, self.final_hypothesis)
        self.saver.new_recognition(createUniqueID(self.id + 1))
        self.saver.add_pcm(self.chunk)
        self.saver.final_hypothesis(self.chunk_id, self.final_hypothesis)

        message = parseSaverMessage(self.socket.sent_message)
        self.assertEquals(self.id + 1, uniqId2Int(message.id))
        self.assertEquals(self.chunk, message.body)

    def test_saver_doesnt_save_anything_when_wav_is_empty(self):
        self.saver.new_recognition(createUniqueID(self.id))
        self.saver.final_hypothesis(self.chunk_id, self.final_hypothesis)

        self.assertEquals(self.socket.sent_message, None)


class ASRSpy:

    def __init__(self, final_hypothesis, interim_hypothesis):
        self.processed_chunks = []
        self.final_hypothesis = final_hypothesis
        self.interim_hypothesis = interim_hypothesis
        self.resetted = False
        self.lm = None

    def recognize_chunk(self, chunk):
        self.processed_chunks.append(chunk)

        return self.interim_hypothesis

    def get_final_hypothesis(self):
        return self.final_hypothesis

    def change_lm(self, lm):
        self.lm = lm

    def reset(self):
        self.resetted = True


class DummyAudio:

    def __init__(self):
        self.splitted_chunks = []
        self.resetted = False

    def load_wav_from_string_as_pcm(self, string):
        return "pcm " + string

    def resample_to_default_sample_rate(self, pcm, sample_rate):
        return "resampled " + pcm

    def set_chunks(self, splitted_chunks):
        self.splitted_chunks = splitted_chunks

    def chunks(self, pcm, sample_rate):
        if len(self.splitted_chunks) > 0:
            for dummy_pcm in self.splitted_chunks:
                yield dummy_pcm, "resampled" + dummy_pcm
        else:
            yield pcm, "resampled " + pcm

    def reset(self):
        self.resetted = True

class SaverSpy:

    def __init__(self):
        self.saved_data = {}

    def new_recognition(self, id, frame_rate=16000):
        self.id = self.parse_id(id)
        self.saved_data[self.id] = {"frame_rate": frame_rate, "chunks": []}
        self.current_chunk = {"chunk_id": "", "pcm": "", "hypothesis": ""}

    def add_pcm(self, pcm):
        self.current_chunk["pcm"] += pcm

    def final_hypothesis(self, chunk_id, final_hypothesis):
        self.current_chunk["chunk_id"] = chunk_id
        self.current_chunk["hypothesis"] = final_hypothesis
        self.saved_data[self.id]["chunks"].append(self.current_chunk)

        self.current_chunk = {"chunk_id": "", "pcm": "", "hypothesis": ""}

    def parse_id(self, id):
        return uniqId2Int(id)


class VADDummy:

    def __init__(self):
        self.data = []
        self.messages = []
        self.resetted = False

    def set_messages(self, messages):
        self.messages = messages

    def decide(self, original_pcm, resampled_pcm):
        self.data.append((original_pcm, resampled_pcm))

        if len(self.messages) > 0:
            return self.messages.pop(0)
        else:
            return True, None, original_pcm, resampled_pcm

    def reset(self):
        self.resetted = True


class IDGeneratorDummy:

    def __init__(self):
        self.ids = []

    def set_ids(self, ids):
        self.ids = ids

    def __call__(self):
        if len(self.ids) > 0:
            return self.ids.pop(0)
        else:
            return 0
