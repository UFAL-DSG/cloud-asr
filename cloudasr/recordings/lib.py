import os
import re
import uuid
import zmq.green as zmq
from cloudasr.models import UsersModel, RecordingsModel
from cloudasr.messages.helpers import *

def create_recordings_saver(address, model):
    def create_socket():
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind(address)

        return socket

    run_forever = lambda: True

    return RecordingsSaver(create_socket, model, run_forever)


class RecordingsSaver:

    def __init__(self, create_socket, model, should_continue):
        self.create_socket = create_socket
        self.model = model
        self.should_continue = should_continue

    def run(self):
        self.socket = self.create_socket()

        while self.should_continue():
            recording = parseSaverMessage(self.socket.recv())

            id = uniqId2Int(recording.id)
            part = recording.part
            chunk_id = uniqId2Int(recording.chunk_id)
            model = recording.model
            body = recording.body
            frame_rate = recording.frame_rate
            alternatives = alternatives2List(recording.alternatives)

            self.model.save_recording(id, part, chunk_id, model, body, frame_rate, alternatives)
