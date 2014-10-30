from math import *

def create_asr():
    import config
    from kaldi.utils import lattice_to_nbest, wst2dict
    from kaldi.decoders import PyOnlineLatgenRecogniser
    from asr_utils import lattice_calibration

    recogniser = PyOnlineLatgenRecogniser()
    recogniser.setup(config.kaldi_config)
    dictionary = wst2dict(config.wst_path)
    lattice = Lattice(dictionary, lattice_to_nbest, lattice_calibration)

    return ASR(recogniser, lattice)

class ASR:

    def __init__(self, recogniser, lattice):
        self.recogniser = recogniser
        self.lattice = lattice
        self.callbacks = []

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def recognize_chunk(self, chunk):
        decoded_frames = 0
        self.recogniser.frame_in(chunk)
        dec_t = self.recogniser.decode(max_frames=10)
        while dec_t > 0:
            self.call_callbacks()

            decoded_frames += dec_t
            dec_t = self.recogniser.decode(max_frames=10)

        return (0.0, u"Not Implemented Yet")

    def get_final_hypothesis(self):
        self.recogniser.prune_final()
        utt_lik, lat = self.recogniser.get_lattice()
        self.recogniser.reset()

        return self.lattice.to_nbest(lat, 10)

    def call_callbacks(self):
        for callback in self.callbacks:
            callback()


class Lattice:

    def __init__(self, dictionary, lattice_to_nbest, lattice_calibration):
        self.dictionary = dictionary
        self.lattice_to_nbest = lattice_to_nbest
        self.lattice_calibration = lattice_calibration

    def to_nbest(self, lattice, n):
        return [(exp(-prob), self.path_to_text(path)) for (prob, path) in self.lattice_to_nbest(self.lattice_calibration(lattice), n=n)]

    def path_to_text(self, path):
        return u' '.join([unicode(self.dictionary[w]) for w in path])
