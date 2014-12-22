import os
import urllib2
import StringIO
import unittest
import json
from jsonschema import validate


class TestBatchRecognition(unittest.TestCase):

    def test_batch_recognition(self):
        response = self.get_response_for_wav()

        self.assertResponseHasCorrectSchema(response)

    def get_response_for_wav(self):
        url = "http://127.0.0.1:8000/recognize?lang=en-towninfo"
        wav = self.load_wav()
        headers = {"Content-Type": "audio/x-wav; rate=16000;"}
        request = urllib2.Request(url, wav, headers)

        return urllib2.urlopen(request).read()

    def load_wav(self):
        basedir = os.path.dirname(os.path.realpath(__file__))
        return open("%s/../resources/test.wav" % basedir, "rb").read()

    def assertResponseHasCorrectSchema(self, response):
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

        validationResult = validate(json.loads(response), schema)
        self.assertIsNone(validationResult, msg="Response has invalid schema")
