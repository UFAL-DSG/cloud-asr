from math import *

def create_asr():
    from alex_asr.utils import lattice_to_nbest
    from alex_asr import Decoder

    recogniser = Decoder("/model")
    lattice_to_nbest_func = lambda lattice, n: lattice_to_nbest(lattice, n)

    return ASR(recogniser, lattice_to_nbest_func)

class ASR:

    def __init__(self, recogniser, lattice_to_nbest):
        self.recogniser = recogniser
        self.lattice_to_nbest = lattice_to_nbest
        self.decoded_frames = 0
        self.callbacks = []

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def recognize_chunk(self, chunk):
        self.recogniser.accept_audio(chunk)
        dec_t = self.recogniser.decode(max_frames=10)
        while dec_t > 0:
            self.call_callbacks()

            self.decoded_frames += dec_t
            dec_t = self.recogniser.decode(max_frames=10)

        if self.decoded_frames == 0:
            return (1.0, '')
        else:
            p, interim_result = self.recogniser.get_best_path()
            return p, self._tokens_to_words(interim_result)

    def _tokens_to_words(self, tokens):
        print tokens
        return " ".join([self.recogniser.get_word(x).decode('utf8') for x in tokens])

    def get_final_hypothesis(self):
        if self.decoded_frames == 0:
            return [(1.0, '')]

        self.recogniser.finalize_decoding()
        utt_lik, lat = self.recogniser.get_lattice()
        self.reset()

        return self._to_nbest(lat, 10)

    def _to_nbest(self, lattice, n):
        return [(exp(-prob), self._tokens_to_words(path)) for (prob, path) in self.lattice_to_nbest(lattice, n=n)]

    def change_lm(self, lm):
        pass

    def reset(self):
        self.decoded_frames = 0
        self.recogniser.reset()

    def call_callbacks(self):
        for callback in self.callbacks:
            callback()
