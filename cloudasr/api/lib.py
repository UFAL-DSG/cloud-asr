import base64
import struct
import zmq.green as zmq
import re
import uuid
from cloudasr.messages import MasterResponseMessage
from cloudasr.messages.helpers import *

def create_frontend_worker(master_address):
    context = zmq.Context()
    master_socket = context.socket(zmq.REQ)
    master_socket.connect(master_address)
    worker_socket = context.socket(zmq.REQ)
    decoder = Decoder()
    id_generator = lambda: uuid.uuid4().int

    return FrontendWorker(master_socket, worker_socket, decoder, id_generator)


class FrontendWorker:
    def __init__(self, master_socket, worker_socket, decoder, id_generator):
        self.master_socket = master_socket
        self.worker_socket = worker_socket
        self.decoder = decoder
        self.id_generator = id_generator
        self.id = None

    def close(self):
        self.master_socket.close()
        self.worker_socket.close()

    def recognize_batch(self, data, headers):
        self.validate_headers(headers)
        self.connect_to_worker(data["model"])

        frame_rate = self.extract_frame_rate_from_headers(headers)
        response = self.recognize_batch_on_worker(data, frame_rate)

        return response

    def connect_to_worker(self, model):
        self.id = self.id_generator()
        self.worker_address = self.get_worker_address_from_master(model)
        self.worker_socket.connect(self.worker_address)

    def recognize_chunk(self, data, frame_rate):
        chunk = self.decoder.decode(data)
        self.send_request_to_worker(chunk, "ONLINE", frame_rate, has_next = True)
        response = self.read_response_from_worker()

        return self.format_response(response.results, self.format_online_recognition_response)

    def format_response(self, results, formatter):
        if any([result.status == ResultsMessage.ERROR for result in results]):
            raise WorkerInternalError

        return [formatter(result) for result in results]

    def change_lm(self, lm):
        self.send_request_to_worker(b"", "ONLINE", frame_rate = 44100, has_next = True, new_lm = lm)
        response = self.read_response_from_worker()

        return self.format_response(response.results, self.format_online_recognition_response)

    def end_recognition(self):
        self.send_request_to_worker(b"", "ONLINE", frame_rate = 44100, has_next = False)
        response = self.read_response_from_worker()
        self.worker_socket.disconnect(self.worker_address)

        return self.format_response(response.results, self.format_online_recognition_response)


    def validate_headers(self, headers):
        if "Content-Type" not in headers:
            raise MissingHeaderError()

        if not re.match("audio/x-wav; rate=\d+;", headers["Content-Type"]):
            raise MissingHeaderError()

    def extract_frame_rate_from_headers(self, headers):
        return int(re.search("audio/x-wav; rate=(\d+);", headers["Content-Type"]).group(1))

    def get_worker_address_from_master(self, model):
        request = createWorkerRequestMessage(model)
        self.master_socket.send(request.SerializeToString())
        response = parseMasterResponseMessage(self.master_socket.recv())

        if response.status == MasterResponseMessage.SUCCESS:
            return response.address
        else:
            raise NoWorkerAvailableError()

    def recognize_batch_on_worker(self, data, frame_rate):
        self.send_request_to_worker(data["wav"], "BATCH", frame_rate, has_next = False, new_lm = data["lm"])
        response = self.read_response_from_worker()
        self.worker_socket.disconnect(self.worker_address)

        return self.format_response(response.results, self.format_batch_recognition_response)

    def send_request_to_worker(self, data, type, frame_rate = None, has_next = False, new_lm = ""):
        request = createRecognitionRequestMessage(type, data, has_next, self.id, frame_rate, new_lm)
        self.worker_socket.send(request.SerializeToString())

    def read_response_from_worker(self):
        response = parseResultsMessage(self.worker_socket.recv())
        return response

    def format_batch_recognition_response(self, response):
        return {
            "result": [
                {
                    "alternative": [{"confidence": a.confidence, "transcript": a.transcript} for a in response.alternatives],
                    "final": response.final,
                },
            ],
            "result_index": 0,
            "chunk_id": str(uniqId2Int(response.id)),
            "request_id": str(self.id)
        }

    def format_online_recognition_response(self, response):
        return {
            'status': 0,
            'result': {
                'hypotheses': [{"confidence": a.confidence, "transcript": a.transcript} for a in response.alternatives],
            },
            'final': response.final,
            'chunk_id': str(uniqId2Int(response.id)),
            'request_id': str(self.id)
        }

class Decoder:

    def decode(self, data):
        return base64.b64decode(data)

class NoWorkerAvailableError(Exception):
    pass

class MissingHeaderError(Exception):
    pass

class WorkerInternalError(Exception):
    pass
