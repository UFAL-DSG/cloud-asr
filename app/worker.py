from asr import asr_init, recognize_wav, create_response
import os
import zmq
from datetime import datetime

def log(message):
    print "%s\t%s" % (str(datetime.now()), message)

log('Loading models.')
basedir = os.path.dirname(os.path.realpath(__file__))
asr_init(basedir)
log('Models loaded.')

port = "5560"
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.connect("tcp://localhost:%s" % port)

log('Worker initialized.')

while True:
    wav = socket.recv()
    log('Received wav for speech recognition.')
    best_hypotheses = recognize_wav(wav)
    socket.send_json(create_response(best_hypotheses))
    log('Recognized hypotheses sent.')

