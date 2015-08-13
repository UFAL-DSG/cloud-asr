import unittest
from types import *
from asr import ASR
from lib import AudioUtils

class TestASR(unittest.TestCase):

    def setUp(self):
        self.recogniser = DummyRecogniser()
        self.asr = ASR(self.recogniser, dummy_to_nbest, dummy_to_best_path)

    def test_asr_returns_empty_final_hypothesis_when_nothing_was_decoded(self):
        final_hypothesis = self.asr.get_final_hypothesis()
        self.assertEqual([(1.0, '')], final_hypothesis)

    def test_asr_returns_empty_interim_hypothesis_when_nothing_was_decode(self):
        interim_hypothesis = self.asr.recognize_chunk(b'')
        self.assertEqual((1.0, ''), interim_hypothesis)

    def test_asr_returns_dummy_final_hypothesis(self):
        interim_hypothesis = self.asr.recognize_chunk(self.load_pcm_sample_data())
        final_hypothesis = self.asr.get_final_hypothesis()

        self.assertEqual(type(final_hypothesis), ListType)
        self.assertGreater(len(final_hypothesis), 0)
        for hypothesis in final_hypothesis:

            self.assertEqual(type(hypothesis[0]), FloatType)
            self.assertEqual(type(hypothesis[1]), UnicodeType)
            self.assertGreaterEqual(hypothesis[0], 0)

    def test_recognize_chunk_returns_interim_results(self):
        interim_hypothesis = self.asr.recognize_chunk(self.load_pcm_sample_data())

        self.assertEquals(type(interim_hypothesis[0]), FloatType)
        self.assertEquals(type(interim_hypothesis[1]), UnicodeType)

    def test_recognize_chunk_calls_callback(self):
        self.callback_called = False
        self.asr.add_callback(self.callback)
        self.asr.recognize_chunk(self.load_pcm_sample_data())

        self.assertTrue(self.callback_called)

    def test_reset_resets_pipeline(self):
        self.asr.reset()
        self.assertTrue(self.recogniser.resetted)

    def load_pcm_sample_data(self):
        audio = AudioUtils()

        return audio.load_wav_from_file_as_pcm("./resources/test.wav")

    def callback(self):
        self.callback_called = True

class DummyRecogniser:

    def __init__(self):
        self.frames = 100
        self.resetted = False

    def frame_in(self, frame):
        self.frames = len(frame)

    def decode(self, max_frames = 0):
        self.frames = max(self.frames - max_frames, 0)
        return self.frames

    def finalize_decoding(self):
        pass

    def get_lattice(self):
        return (None, None)

    def get_best_path(self):
        return (None, None)

    def reset(self, reset_pipeline):
        self.resetted = True


def dummy_to_nbest(lattice, n):
    return [(1.0, u"Hello World!")]

def dummy_to_best_path(path):
    return (0.0, u"Interim Result")
