def create_vad():
    return DummyVAD()

class DummyVAD:

    def reset(self):
        pass

    def decide(self, original_frames, resampled_frames):
        return True, None, b'', b''
