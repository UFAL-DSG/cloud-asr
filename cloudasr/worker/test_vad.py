import unittest
import audioop
import math
import wave
from vad import create_vad
from lib import AudioUtils

class TestVAD(unittest.TestCase):

    def test_vad(self):
        vad = create_vad(16000)

        utterances = 0
        for original_chunk, resampled_chunk in self.chunks():
            _, change, _, _ = vad.decide(original_chunk, resampled_chunk)

            if change == 'speech':
               utterances += 1

        self.assertEqual(3, utterances)

    def chunks(self):
        wav = wave.open("/opt/resources/test2.wav", "rb")
        pcm = wav.readframes(wav.getnframes())

        audio_utils = AudioUtils(16000)
        return audio_utils.chunks(pcm, 44100)
