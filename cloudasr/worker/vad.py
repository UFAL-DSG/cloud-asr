import webrtcvad
import collections

def create_vad(sample_rate):
    return VAD(sample_rate)

class VAD:

    def __init__(self, sample_rate=16000, level=0):
        self.vad = webrtcvad.Vad(level)
        self.sample_rate = int(sample_rate)
        self.num_padding_frames = 10
        self.reset()

    def reset(self):
        self.triggered = False
        self.ring_buffer = collections.deque(maxlen=self.num_padding_frames)

    def decide(self, original_frame, resampled_frame):
        change = None

        self.ring_buffer.append((resampled_frame, original_frame))
        if not self.triggered:
            num_voiced = len([f for f in self.ring_buffer if self.vad.is_speech(f[0], self.sample_rate)])
            if num_voiced > 0.9 * self.ring_buffer.maxlen:
                self.triggered = True
                resampled_frame = b"".join([f[0] for f in self.ring_buffer])
                original_frame = b"".join([f[1] for f in self.ring_buffer])
                change = "speech"
                self.ring_buffer.clear()
        else:
            num_unvoiced = len([f for f in self.ring_buffer if not self.vad.is_speech(f[0], self.sample_rate)])

            if num_unvoiced > 0.9 * self.ring_buffer.maxlen:
                self.triggered = False
                change = "non-speech"
                self.ring_buffer.clear()

        return self.triggered, change, original_frame, resampled_frame
