import os
import time
import wave
import json
import struct
import base64
import urllib2
import unittest
from jsonschema import validate
from websocket import create_connection


class TestOnlineRecognition(unittest.TestCase):

    def setUp(self):
        self.socket = create_connection('ws://localhost:8000/transcribe-online')
        self.received_responses = 0
        self.expected_responses = 0
        time.sleep(1)

    def test_online_recognition(self):
        self.send_chunks()
        self.assertEquals(self.expected_responses + 1, self.received_responses)

    def send_chunks(self):
        self.socket.send('en-towninfo')
        self.socket.send('16000')

        for chunk in self.chunks():
            self.socket.send_binary(chunk)
            self.assertMessageHasCorrectSchema(self.socket.recv())

        self.socket.send_binary("")
        self.assertMessageHasCorrectSchema(self.socket.recv())

    def chunks(self):
        basedir = os.path.dirname(os.path.realpath(__file__))
        wav = wave.open("%s/../resources/test.wav" % basedir, "rb")

        while True:
            frames = wav.readframes(16384)
            if len(frames) == 0:
                break

            self.expected_responses += 1
            yield frames

    def assertMessageHasCorrectSchema(self, message):
        message = json.loads(message)

        schema = {
            "type": "object",
            "properties": {
                "status": {"type": "number"},
                "final": {"type": "boolean"},
                "chunk_id": {"type": "string"},
                "request_id": {"type": "string"},
                "result": {
                    "type": "object",
                    "properties": {
                        "hypotheses": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "transcript": {"type": "string"},
                                    "confidence": {"type": "number"}
                                },
                                "required": ["transcript"],
                                "additionalProperties": False,
                            }
                        }
                    },
                    "required": ["hypotheses"],
                    "additionalProperties": False,
                },

            },
            "required": ["status", "result", "final", "request_id"],
            "additionalProperties": False,
        }

        validationResult = validate(message, schema)
        self.assertIsNone(validationResult, msg="Message has invalid schema")
        self.received_responses += 1
