import os
import urllib2
import StringIO
import unittest
from jsonschema import validate
from socketIO_client import SocketIO


class TestOnlineRecognition(unittest.TestCase):


    def setUp(self):
        self.socketIO = SocketIO('localhost', 8000)
        self.received_responses = 0

    def test_online_recognition(self):
        self.socketIO.on('result', self.assertMessageHasCorrectSchema)
        self.send_chunks()
        self.assertEquals(len(self.chunks()), self.received_responses)

    def send_chunks(self):
        self.socketIO.emit('begin', {'model': 'en-GB'})

        for chunk in self.chunks():
            self.socketIO.emit('chunk', {'chunk': chunk})
            self.socketIO.wait_for_callbacks()

        self.socketIO.emit('end', {})
        self.socketIO.wait_for_callbacks()

    def chunks(self):
        return range(1,10)

    def assertMessageHasCorrectSchema(self, message):
        schema = {
            "type": "object",
            "properties": {
                "status": {"type": "number"},
                "final": {"type": "boolean"},
                "result": {
                    "type": "object",
                    "properties": {
                        "hypotheses": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "transcript": {"type": "string"}
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
            "required": ["status", "result", "final"],
            "additionalProperties": False,
        }

        validationResult = validate(message, schema)
        self.assertIsNone(validationResult, msg="Message has invalid schema")
        self.received_responses += 1


