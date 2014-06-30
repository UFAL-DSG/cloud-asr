import wave
import struct
from StringIO import StringIO
from background_asr import recognize_wav

class OnlineASR:
    def __init__(self, emit):
        self.socket = 12345
        self.emit = emit
        self.pcm = []

    def recognize_chunk(self, message):
        for i in message['chunk']:
            self.pcm.append(struct.pack('h', i))

        self.emit('result', {'result':[]})

    def end(self):
        f = StringIO()
        wav = wave.open(f, 'wb')
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        wav.writeframes(b''.join(self.pcm))

        self.emit('result', recognize_wav(f.getvalue()))
        self.emit('end', {})

        wav.close()
        f.close()
