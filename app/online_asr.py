class OnlineASR:
    def __init__(self, emit):
        self.socket = 12345
        self.emit = emit

    def recognize_chunk(self, message):
        self.emit('result', {'result':[]})

    def end(self):
        self.emit('result', {
            "result": [
                {
                    "alternative": [{"transcript": "Hello World!", "confidence": 1.0}],
                    "final": True,
                },
            ],
            "result_index": 0
        })
        self.emit('end', {})
