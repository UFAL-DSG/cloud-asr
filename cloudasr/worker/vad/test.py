import unittest
import audioop
import wave
import theano
from vad import VAD
from ffnn import FFNNVAD

theano.config.mode = 'FAST_COMPILE'

class TestVAD(unittest.TestCase):

    def test_vad(self):
        vad = self.create_vad()

        utterances = 0
        for chunk in self.chunks():
            _, change, _ = vad.decide(chunk)

            if change == 'speech':
               utterances += 1

        self.assertEqual(3, utterances)

    def create_vad(self):
        cfg = {
            'sample_rate': 44100,
            'frontend': 'MFCC',
            'framesize': 512,
            'frameshift': 160,
            'usehamming': True,
            'preemcoef': 0.97,
            'numchans': 26,
            'ceplifter': 22,
            'numceps': 12,
            'enormalise': True,
            'zmeansource': True,
            'usepower': True,
            'usec0': False,
            'usecmn': False,
            'usedelta': False,
            'useacc': False,
            'n_last_frames': 30, # 15,
            'n_prev_frames': 15,
            'mel_banks_only': True,
            'lofreq': 125,
            'hifreq': 3800,
            'model': '/opt/models/vad.tffnn',
            'filter_length': 2,
        }

        return VAD(FFNNVAD(cfg))

    def chunks(self):
        wav = wave.open("/opt/resources/test2.wav", "rb")

        while True:
            frames = wav.readframes(256)
            if len(frames) == 0:
                break

            yield self.resample_to_default_sample_rate(frames)

    def resample_to_default_sample_rate(self, pcm):
        pcm, state = audioop.ratecv(pcm, 2, 1, 44100, 16000, None)

        return pcm
