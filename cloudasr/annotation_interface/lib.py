import os
import re
import json
import wave
import zmq.green as zmq
from cloudasr.messages.helpers import *

def create_recordings_saver(address, path):
    def create_socket():
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind(address)

        return socket

    file_saver = FileSaver(path)
    run_forever = lambda: True

    return RecordingsSaver(create_socket, file_saver, run_forever)


class RecordingsSaver:

    def __init__(self, create_socket, file_saver, should_continue):
        self.create_socket = create_socket
        self.file_saver = file_saver
        self.should_continue = should_continue

    def run(self):
        self.socket = self.create_socket()

        while self.should_continue():
            recording = parseSaverMessage(self.socket.recv())

            id = uniqId2Int(recording.id)
            model = recording.model
            body = recording.body
            frame_rate = recording.frame_rate
            alternatives = alternatives2List(recording.alternatives)

            self.file_saver.save(id, model, body, frame_rate, alternatives)


class FileSaver:

    def __init__(self, path):
        self.path = path

    def save(self, id, model, body, frame_rate, alternatives):
        self.save_wav(id, model, body, frame_rate)
        self.save_hypothesis(id, model, alternatives)

    def save_wav(self, id, model, body, frame_rate):
        wav = wave.open('%s/%s-%d.wav' % (self.path, model, id), 'w')
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(frame_rate)
        wav.writeframes(body)
        wav.close()

    def save_hypothesis(self, id, model, alternatives):
        json.dump(alternatives, open('%s/%s-%d.json' % (self.path, model, id), 'w'))


class RecordingsModel:

    def __init__(self, path):
        self.path = path

    def get_recordings(self):
        recordings = [f for f in os.listdir(self.path) if f.endswith('wav')]
        recordings_data = []

        for recording in recordings:
            search = re.search("^([a-z-]+)-(\d+)\.wav$", recording)
            wav_url = "/static/data/%s" % recording
            hypothesis = json.load(open('%s/%s-%s.json' % (self.path, search.group(1), search.group(2))))

            recordings_data.append({
                'id': search.group(2),
                'model': search.group(1),
                'wav_url': wav_url,
                'hypothesis': hypothesis[0][1]
            })

        return recordings_data
