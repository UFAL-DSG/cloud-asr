def create_asr():
    return DummyASR()

class DummyASR:

    def add_callback(self, callback):
        pass

    def recognize_chunk(self, chunk):
        return (1.0, 'Dummy interim result')

    def get_final_hypothesis(self):
        return [(1.0, 'Dummy final result')]

    def reset(self):
        pass
