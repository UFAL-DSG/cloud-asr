import os
import base64
import urllib2
import unittest
import wave
import struct
from jsonschema import validate
from socketIO_client import SocketIO


class TestOnlineRecognition(unittest.TestCase):

    def setUp(self):
        self.socketIO = SocketIO('localhost', 8000)
        self.received_responses = 0
        self.expected_responses = 0

    def test_online_recognition(self):
        self.socketIO.on('result', self.assertMessageHasCorrectSchema)
        self.socketIO.on('final_result', self.assertFinalResultHasCorrectSchema)
        self.send_chunks()
        self.assertEquals(self.expected_responses, self.received_responses)

    def send_chunks(self):
        self.socketIO.emit('begin', {'model': 'en-towninfo'})

        for chunk in self.chunks():
            self.socketIO.emit('chunk', {'chunk': chunk, 'frame_rate': 16000})
            self.socketIO.wait_for_callbacks()

        self.socketIO.emit('end', {})
        self.socketIO.wait_for_callbacks()
        self.socketIO.wait_for_callbacks()

    def chunks(self):
        basedir = os.path.dirname(os.path.realpath(__file__))
        wav = wave.open("%s/../resources/test.wav" % basedir, "rb")

        while True:
            frames = wav.readframes(16384)
            if len(frames) == 0:
                break

            self.expected_responses += 1
            yield self.serialize_frames(frames)

    def serialize_frames(self, frames):
        pcm = [struct.unpack('H', frames[i:i+2])[0] for i in range(0, len(frames), 2)]
        data = []
        for p in pcm:
            data.append(unichr(p & 255))
            data.append(unichr(p >> 8))

        return ''.join(data)

    def assertMessageHasCorrectSchema(self, message):
        schema = {
            "type": "object",
            "properties": {
                "status": {"type": "number"},
                "final": {"type": "boolean"},
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

    def assertFinalResultHasCorrectSchema(self, message):
        schema = {
            "type": "object",
            "properties": {
                "result": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "alternative": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "confidence": {"type": "number"},
                                        "transcript": {"type": "string"},
                                    },
                                    "required": ["confidence", "transcript"],
                                    "additionalProperties": False,
                                },
                                "minItems": 1,
                            },
                            "final": {"type": "boolean"},
                        },
                        "required": ["alternative", "final"],
                        "additionalProperties": False,
                    },
                    "minItems": 1,
                },
                "result_index": {"type": "number"},
                "request_id": {"type": "string"},
            },
            "required": ["result", "result_index", "request_id"],
            "additionalProperties": False,
        }

        validationResult = validate(message, schema)
        self.assertIsNone(validationResult, msg="Response has invalid schema")
