from math import *

def create_asr():
    import config
    from kaldi.utils import lattice_to_nbest, wst2dict
    from kaldi.decoders import PyOnlineLatgenRecogniser
    from asr_utils import lattice_calibration

    recogniser = PyOnlineLatgenRecogniser()
    recogniser.setup(config.kaldi_config)
    dictionary = wst2dict(config.wst_path)

    path_to_text = PathToText(dictionary)
    to_nbest = ToNBest(path_to_text, lattice_to_nbest, lattice_calibration)
    to_best_path = ToBestPath(path_to_text)

    return ASR(recogniser, to_nbest, to_best_path)

class ASR:

    def __init__(self, recogniser, to_nbest, to_best_path):
        self.recogniser = recogniser
        self.to_nbest = to_nbest
        self.to_best_path = to_best_path
        self.decoded_frames = 0
        self.callbacks = []

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def recognize_chunk(self, chunk):
        self.recogniser.frame_in(chunk)
        dec_t = self.recogniser.decode(max_frames=10)
        while dec_t > 0:
            self.call_callbacks()

            self.decoded_frames += dec_t
            dec_t = self.recogniser.decode(max_frames=10)

        if self.decoded_frames == 0:
            return (1.0, '')
        else:
            interim_result = self.recogniser.get_best_path()
            return self.to_best_path(interim_result)

    def get_final_hypothesis(self):
        if self.decoded_frames == 0:
            return [(1.0, '')]

        self.recogniser.finalize_decoding()
        utt_lik, lat = self.recogniser.get_lattice()
        self.reset()

        return self.to_nbest(lat, 10)

    def change_lm(self, lm):
        pass

    def reset(self):
        self.decoded_frames = 0
        self.recogniser.reset(reset_pipeline=True)

    def call_callbacks(self):
        for callback in self.callbacks:
            callback()



class ToNBest:

    def __init__(self, path_to_text, lattice_to_nbest, lattice_calibration):
        self.path_to_text = path_to_text
        self.lattice_to_nbest = lattice_to_nbest
        self.lattice_calibration = lattice_calibration

    def __call__(self, lattice, n):
        return [(exp(-prob), self.path_to_text(path)) for (prob, path) in self.lattice_to_nbest(self.lattice_calibration(lattice), n=n)]

class ToBestPath:

    def __init__(self, path_to_text):
        self.path_to_text = path_to_text

    def __call__(self, best_path):
        (prob, path) = best_path
        return (prob, self.path_to_text(path))

class PathToText:

    def __init__(self, dictionary):
        self.dictionary = dictionary

    def __call__(self, path):
        return u' '.join([unicode(self.dictionary[w]) for w in path])
