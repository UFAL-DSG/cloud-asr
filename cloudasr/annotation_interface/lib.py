import os
import re
import json
import uuid
import wave
import zmq.green as zmq
from schema import create_db_session, Recording, Transcription
from cloudasr.messages.helpers import *

def create_recordings_saver(address, path, model):
    def create_socket():
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind(address)

        return socket

    run_forever = lambda: True

    return RecordingsSaver(create_socket, model, run_forever)

def create_db_connection(path):
    return create_db_session(path)


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
            model = recording.model
            body = recording.body
            frame_rate = recording.frame_rate
            alternatives = alternatives2List(recording.alternatives)

            self.model.save_recording(id, model, body, frame_rate, alternatives)


class RecordingsModel:

    def __init__(self, path, db):
        self.db = db
        self.path = path
        self.file_saver = FileSaver(path)

    def get_recordings(self):
        return self.db.query(Recording).all()

    def get_recording(self, id):
        return self.db.query(Recording).filter(Recording.id == int(id)).one()

    def save_recording(self, id, model, body, frame_rate, alternatives):
        (path, url) = self.file_saver.save_wav(id, model, body, frame_rate)
        self.save_recording_to_db(id, model, path, url, alternatives)

    def save_recording_to_db(self, id, model, path, url, alternatives):
        recording = Recording(
            id = id,
            model = model,
            path = path,
            url = url,
            hypothesis = alternatives[0][1],
            confidence = alternatives[0][0]
        )

        self.db.add(recording)
        self.db.commit()

    def add_transcription(self, id, transcription):
        transcription = Transcription(
            user_id = 1,
            text = transcription
        )

        recording = self.get_recording(id)
        recording.transcriptions.append(transcription)
        self.db.commit()


class FileSaver:

    def __init__(self, path):
        self.path = path

    def save_wav(self, id, model, body, frame_rate):
        path = '%s/%s-%d.wav' % (self.path, model, id)
        url = '/static/data/%s-%d.wav' % (model, id)

        wav = wave.open(path, 'w')
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(frame_rate)
        wav.writeframes(body)
        wav.close()

        return (path, url)

    def save_hypothesis(self, id, model, alternatives):
        json.dump(alternatives, open('%s/%s-%d.json' % (self.path, model, id), 'w'))


