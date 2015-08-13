import unittest
import audioop
import wave
import theano
from vad import create_vad

theano.config.mode = 'FAST_COMPILE'

class TestVAD(unittest.TestCase):

    def test_vad(self):
        vad = create_vad()

        utterances = 0
        for original_chunk, resampled_chunk in self.chunks():
            _, change, _, _ = vad.decide(original_chunk, resampled_chunk)

            if change == 'speech':
               utterances += 1

        self.assertEqual(3, utterances)

    def chunks(self):
        wav = wave.open("/opt/resources/test2.wav", "rb")

        while True:
            frames = wav.readframes(512)
            if len(frames) == 0:
                break

            yield frames, self.resample_to_default_sample_rate(frames)

    def resample_to_default_sample_rate(self, pcm):
        pcm, state = audioop.ratecv(pcm, 2, 1, 44100, 16000, None)

        return pcm
