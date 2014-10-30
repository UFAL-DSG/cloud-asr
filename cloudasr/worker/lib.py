import audioop
import wave
import zmq
import time
from StringIO import StringIO
from asr import create_asr
from cloudasr.messages import RecognitionRequestMessage
from cloudasr.messages.helpers import *


def create_worker(model, frontend_address, public_address, master_address):
    poller = create_poller(frontend_address)
    heartbeat = create_heartbeat(model, public_address, master_address)
    asr = create_asr()
    audio = AudioUtils()
    run_forever = lambda: True

    return Worker(poller, heartbeat, asr, audio, run_forever)

def create_poller(frontend_address):
    from cloudasr import Poller
    context = zmq.Context()
    frontend_socket = context.socket(zmq.REP)
    frontend_socket.bind(frontend_address)

    sockets = {
        "frontend": {"socket": frontend_socket, "receive": frontend_socket.recv, "send": frontend_socket.send},
    }
    time_func = time.time

    return Poller(sockets, time_func)

def create_heartbeat(model, address, master_address):
    context = zmq.Context()
    master_socket = context.socket(zmq.PUSH)
    master_socket.connect(master_address)

    return Heartbeat(model, address, master_socket)


class Worker:

    def __init__(self, poller, heartbeat, asr, audio, should_continue):
        self.poller = poller
        self.heartbeat = heartbeat
        self.asr = asr
        self.audio = audio
        self.should_continue = should_continue

    def run(self):
        self.heartbeat.send("READY")

        while self.should_continue():
            messages, time = self.poller.poll(1000)

            if "frontend" in messages:
                self.handle_request(messages["frontend"])
            else:
                self.heartbeat.send("READY")

    def handle_request(self, message):
        request = parseRecognitionRequestMessage(message)

        if request.type == RecognitionRequestMessage.BATCH:
            self.handle_batch_request(request)
        else:
            request_id = request.id
            has_next = True

            while True:
                if request_id == request.id:
                    has_next = self.handle_online_request(request)
                else:
                    self.handle_bad_chunk()

                if not has_next:
                    break

                messages, time = self.poller.poll(10000)
                if "frontend" in messages:
                    request = parseRecognitionRequestMessage(messages["frontend"])
                else:
                    self.heartbeat.send("FINISHED")
                    break


    def handle_batch_request(self, request):
        pcm = self.get_pcm_from_message(request.body)
        self.asr.recognize_chunk(pcm)
        final_hypothesis = self.asr.get_final_hypothesis()
        response = self.create_final_response(final_hypothesis)

        self.poller.send("frontend", response.SerializeToString())
        self.heartbeat.send("FINISHED")

    def handle_online_request(self, request):
        pcm = self.audio.resample_to_default_sample_rate(request.body, request.frame_rate)
        interim_hypothesis = self.asr.recognize_chunk(pcm)

        if request.has_next == True:
            response = self.create_interim_response(interim_hypothesis)
            self.poller.send("frontend", response.SerializeToString())
            self.heartbeat.send("WORKING")
            return True
        else:
            final_hypothesis = self.asr.get_final_hypothesis()
            response = self.create_final_response(final_hypothesis)
            self.poller.send("frontend", response.SerializeToString())
            self.heartbeat.send("FINISHED")
            return False

    def handle_bad_chunk(self):
        self.poller.send("frontend", createErrorResultsMessage().SerializeToString())

    def get_pcm_from_message(self, message):
        return self.audio.load_wav_from_string_as_pcm(message)

    def create_final_response(self, final_hypothesis):
        return createResultsMessage(True, final_hypothesis)

    def create_interim_response(self, interim_hypothesis):
        return createResultsMessage(False, [interim_hypothesis])


class Heartbeat:

    def __init__(self, model, address, socket):
        self.model = model
        self.address = address
        self.socket = socket

    def send(self, status):
        heartbeat = createHeartbeatMessage(self.address, self.model, status)
        self.socket.send(heartbeat.SerializeToString())


class AudioUtils:

    default_sample_width = 2
    default_sample_rate = 16000

    def load_wav_from_string_as_pcm(self, string):
        return self.load_wav_from_file_as_pcm(StringIO(string))

    def load_wav_from_file_as_pcm(self, path):
        return self.convert_wav_to_pcm(self.load_wav(path))

    def load_wav(self, path):
        wav = wave.open(path, 'r')
        if wav.getnchannels() != 1:
            raise Exception('Input wave is not in mono')
        if wav.getsampwidth() != self.default_sample_width:
            raise Exception('Input wave is not in %d Bytes' % def_sample_width)

        return wav

    def convert_wav_to_pcm(self, wav):
        try:
            chunk = 1024
            pcm = b''
            pcmPart = wav.readframes(chunk)

            while pcmPart:
                pcm += str(pcmPart)
                pcmPart = wav.readframes(chunk)

            return self.resample_to_default_sample_rate(pcm, wav.getframerate())
        except EOFError:
            raise Exception('Input PCM is corrupted: End of file.')

    def resample_to_default_sample_rate(self, pcm, sample_rate):
        if sample_rate != self.default_sample_rate:
            pcm, state = audioop.ratecv(pcm, 2, 1, sample_rate, self.default_sample_rate, None)

        return pcm
