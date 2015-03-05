import audioop
import wave
import json
import zmq
import time
from StringIO import StringIO
from asr import create_asr
from vad import create_vad
from cloudasr.messages import RecognitionRequestMessage
from cloudasr.messages.helpers import *


def create_worker(model, hostname, port, master_address, recordings_saver_address):
    poller = create_poller("tcp://0.0.0.0:5678")
    heartbeat = create_heartbeat(model, "tcp://%s:%s" % (hostname, port), master_address)
    asr = create_asr()
    audio = AudioUtils()
    saver = RemoteSaver(create_recordings_saver_socket(recordings_saver_address), model)
    vad = create_vad()
    run_forever = lambda: True

    return Worker(poller, heartbeat, asr, audio, saver, vad, run_forever)

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

def create_recordings_saver_socket(address):
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect(address)

    return socket

def create_heartbeat(model, address, master_address):
    context = zmq.Context()
    master_socket = context.socket(zmq.PUSH)
    master_socket.connect(master_address)

    return Heartbeat(model, address, master_socket)


class Worker:

    def __init__(self, poller, heartbeat, asr, audio, saver, vad, should_continue):
        self.poller = poller
        self.heartbeat = heartbeat
        self.asr = asr
        self.audio = audio
        self.saver = saver
        self.vad = vad
        self.should_continue = should_continue
        self.current_request_id = None

    def run(self):
        self.heartbeat.send("STARTED")

        while self.should_continue():
            messages, time = self.poller.poll(1000)

            if "frontend" in messages:
                self.handle_request(messages["frontend"])
            else:
                if not self.is_online_recognition_running():
                    self.heartbeat.send("WAITING")
                else:
                    self.asr.reset()
                    self.end_online_recognition()
                    self.heartbeat.send("FINISHED")

    def handle_request(self, message):
        request = parseRecognitionRequestMessage(message)

        if request.type == RecognitionRequestMessage.BATCH:
            self.handle_batch_request(request)
        else:
            if not self.is_online_recognition_running():
                self.begin_online_recognition(request)

            if self.is_bad_chunk(request):
                return self.handle_bad_chunk()

            self.handle_online_request(request)

    def handle_batch_request(self, request):
        pcm = self.get_pcm_from_message(request.body)
        resampled_pcm = self.audio.resample_to_default_sample_rate(pcm, request.frame_rate)

        self.asr.recognize_chunk(resampled_pcm)
        final_hypothesis = self.asr.get_final_hypothesis()
        response = self.send_hypothesis(True, final_hypothesis)

        self.saver.new_recognition(request.id)
        self.saver.add_pcm(pcm)
        self.saver.final_hypothesis(final_hypothesis)
        self.heartbeat.send("FINISHED")

    def handle_online_request(self, request):
        pcm = self.audio.resample_to_default_sample_rate(request.body, request.frame_rate)
        vad, change, pcm = self.vad.decide(pcm)

        if vad:
            is_final = False
            hypothesis = [self.asr.recognize_chunk(pcm)]
            self.saver.add_pcm(request.body)
        else:
            is_final = False
            hypothesis = [(1.0, "")]

        if change == "non-speech" or request.has_next == False:
            is_final = True
            hypothesis = self.asr.get_final_hypothesis()

            self.asr.reset()
            self.saver.final_hypothesis(hypothesis)

        self.send_hypothesis(is_final, hypothesis)

        if request.has_next:
            self.heartbeat.send("WORKING")
        else:
            self.end_online_recognition()
            self.heartbeat.send("FINISHED")


    def send_hypothesis(self, is_final, hypothesis):
        response = createResultsMessage(is_final, hypothesis)
        self.poller.send("frontend", response.SerializeToString())

    def is_online_recognition_running(self):
        return self.current_request_id is not None

    def is_bad_chunk(self, request):
        return self.current_request_id != request.id

    def begin_online_recognition(self, request):
        self.current_request_id = request.id
        self.saver.new_recognition(self.current_request_id, request.frame_rate)

    def end_online_recognition(self):
        self.current_request_id = None

    def handle_bad_chunk(self):
        self.poller.send("frontend", createErrorResultsMessage().SerializeToString())

    def get_pcm_from_message(self, message):
        return self.audio.load_wav_from_string_as_pcm(message)


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


class RemoteSaver:

    def __init__(self, socket, model):
        self.socket = socket
        self.model = model
        self.id = None
        self.wav = b""

    def new_recognition(self, id, frame_rate=16000):
        self.id = uniqId2Int(id)
        self.part = 0
        self.frame_rate = frame_rate

    def add_pcm(self, pcm):
        self.wav += pcm

    def final_hypothesis(self, final_hypothesis):
        self.socket.send(createSaverMessage(self.id, self.part, self.model, self.wav, self.frame_rate, final_hypothesis).SerializeToString())
        self.wav = b""
        self.part += 1
