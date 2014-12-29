from cloudasr.messages.helpers import *

class RecordingsSaver:

    def __init__(self, socket, file_saver, should_continue):
        self.socket = socket
        self.file_saver = file_saver
        self.should_continue = should_continue

    def run(self):
        while self.should_continue():
            recording = self.socket.recv()

            id = uniqId2Int(recording.id)
            model = recording.model
            body = recording.body
            frame_rate = recording.frame_rate
            alternatives = alternatives2List(recording.alternatives)

            self.file_saver.save(id, model, body, frame_rate, alternatives)
