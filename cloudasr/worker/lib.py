import audioop
import wave
import zmq
import time
import config
from kaldi.utils import lattice_to_nbest, wst2dict
from kaldi.decoders import PyOnlineLatgenRecogniser
from StringIO import StringIO
from cloudasr.messages import HeartbeatMessage, RecognitionRequestMessage, ResultsMessage


def create_worker(model, frontend_address, public_address, master_address):
    poller = create_poller(frontend_address)
    heartbeat = create_heartbeat(model, public_address, master_address)
    asr = ASR(config.kaldi_config, config.wst_path)
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
        request = RecognitionRequestMessage()
        request.ParseFromString(message)

        if request.type == RecognitionRequestMessage.BATCH:
            pcm = self.get_pcm_from_message(request.body)
            self.asr.recognize_chunk(pcm)
            final_hypothesis = self.asr.get_final_hypothesis()
            response = self.create_response(final_hypothesis)

            self.poller.send("frontend", response.SerializeToString())
            self.heartbeat.send("FINISHED")
        else:
            pcm = self.get_pcm_from_message(request.body)
            interim_hypothesis = self.asr.recognize_chunk(pcm)

            if request.has_next == True:
                response = self.create_interim_response(interim_hypothesis)
                self.poller.send("frontend", response.SerializeToString())
                self.heartbeat.send("WORKING")
            else:
                final_hypothesis = self.asr.get_final_hypothesis()
                response = self.create_response(final_hypothesis)
                self.poller.send("frontend", response.SerializeToString())
                self.heartbeat.send("FINISHED")


    def get_pcm_from_message(self, message):
        return self.audio.load_wav_from_string_as_pcm(message)

    def create_response(self, final_hypothesis):
        response = ResultsMessage()
        response.final = True

        for (confidence, transcript) in final_hypothesis:
            alternative = response.alternatives.add()
            alternative.confidence = confidence
            alternative.transcript = transcript

        return response

    def create_interim_response(self, interim_hypothesis):
        response = ResultsMessage()
        response.final = False

        alternative = response.alternatives.add()
        alternative.confidence = interim_hypothesis[0]
        alternative.transcript = interim_hypothesis[1]

        return response


class Heartbeat:

    def __init__(self, model, address, socket):
        self.model = model
        self.address = address
        self.socket = socket

    def send(self, status):
        statuses = {
            "READY": HeartbeatMessage.READY,
            "WORKING": HeartbeatMessage.WORKING,
            "FINISHED": HeartbeatMessage.FINISHED
        }

        heartbeat = HeartbeatMessage()
        heartbeat.address = self.address
        heartbeat.model = self.model
        heartbeat.status = statuses[status]

        self.socket.send(heartbeat.SerializeToString())


class ASR:

    def __init__(self, kaldi_config, wst_path):
        self.recogniser = PyOnlineLatgenRecogniser()
        self.recogniser.setup(kaldi_config)
        self.wst = wst2dict(wst_path)

    def recognize_chunk(self, chunk):
        decoded_frames = 0
        self.recogniser.frame_in(chunk)
        dec_t = self.recogniser.decode(max_frames=10)
        while dec_t > 0:
            decoded_frames += dec_t
            dec_t = self.recogniser.decode(max_frames=10)

        return (0.0, u"Not Implemented Yet")

    def get_final_hypothesis(self):
        self.recogniser.prune_final()
        utt_lik, lat = self.recogniser.get_lattice()
        self.recogniser.reset()

        return [(prob, self.path_to_text(path)) for (prob, path) in lattice_to_nbest(lat, n=10)]

    def path_to_text(self, path):
        return u' '.join([unicode(self.wst[w]) for w in path])


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
