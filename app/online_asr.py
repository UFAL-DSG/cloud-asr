class OnlineASR:
    def __init__(self, emit):
        self.socket = 12345
        self.emit = emit

    def recognize_chunk(self, message):
        self.emit('result', {'result':[]})

    def end(self):
        self.emit('result', {'result':[]})
        self.emit('end', {})
