from collections import deque
import audioop
import wave

from ffnn import FFNNVAD

class VAD:

    decision_frames_speech = 10
    decision_frames_sil = 10
    speech_buffer_frames = 100

    decision_speech_threshold = 0.7
    decision_non_speech_threshold = 0.1

    def __init__(self, vad_engine):
        self.detection_window_speech = deque(maxlen=self.decision_frames_speech)
        self.detection_window_sil = deque(maxlen=self.decision_frames_sil)
        self.frames = deque(maxlen=self.speech_buffer_frames)
        self.last_vad = False

        self.vad_engine = vad_engine

    def reset(self):
        self.detection_window_speech.clear()
        self.detection_window_sil.clear()
        self.frames.clear()
        self.last_vad = False

    def decide(self, frames):
        self.frames.append(frames)

        decision = self.vad_engine.decide(frames)
        vad, change = self.smoothe_decision(decision)

        return vad, change, self.flush_frames(vad)

    def smoothe_decision(self, decision):
        self.detection_window_speech.append(decision)
        self.detection_window_sil.append(decision)

        speech = float(sum(self.detection_window_speech)) / (len(self.detection_window_speech) + 1.0)
        sil = float(sum(self.detection_window_sil)) / (len(self.detection_window_sil) + 1.0)
        print 'SPEECH: %s SIL: %s' % (speech, sil)

        vad = self.last_vad
        change = None
        if self.last_vad:
            if sil < self.decision_non_speech_threshold:
                vad = False
                change = 'non-speech'
        else:
            if speech > self.decision_speech_threshold:
                vad = True
                change = 'speech'

        self.last_vad = vad

        return vad, change

    def flush_frames(self, vad):
        if vad:
            frames = b''.join(self.frames)
            self.frames.clear()
        else:
            frames = b''

        return frames
