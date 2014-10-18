import math

def create_asr():
    import config
    from kaldi.utils import lattice_to_nbest, wst2dict
    from kaldi.decoders import PyOnlineLatgenRecogniser

    recogniser = PyOnlineLatgenRecogniser()
    recogniser.setup(config.kaldi_config)
    dictionary = wst2dict(config.wst_path)

    return ASR(recogniser, dictionary, lattice_to_nbest)

class ASR:

    def __init__(self, recogniser, dictionary, lattice_to_nbest):
        self.recogniser = recogniser
        self.dictionary = dictionary
        self.lattice_to_nbest = lattice_to_nbest

    def recognize_chunk(self, chunk):
        decoded_frames = 0
        self.recogniser.frame_in(chunk)
        dec_t = self.recogniser.decode(max_frames=10)
        while dec_t > 0:
            decoded_frames += dec_t
            dec_t = self.recogniser.decode(max_frames=10)

        return (0.0, u"Not Implemented Yet")

    def get_final_hypothesis(self):
        self.recogniser.prune_final()
        utt_lik, lat = self.recogniser.get_lattice()
        self.recogniser.reset()

        return [(math.exp(-prob), self.path_to_text(path)) for (prob, path) in self.lattice_to_nbest(lat, n=10)]

    def path_to_text(self, path):
        return u' '.join([unicode(self.dictionary[w]) for w in path])


