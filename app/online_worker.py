from asr import asr_init, recognize_chunk, nbest_hypotheses, create_response, resample_to_def_sample_rate
import os
import zmq
from datetime import datetime

def log(message):
    print "%s\t%s" % (str(datetime.now()), message)

log('Loading models.')
basedir = os.path.dirname(os.path.realpath(__file__))
asr_init(basedir)
log('Models loaded.')

log('Worker initialized.')


while True:
    port = "5660"
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://*:%s" % port)
    log('Socket created')

    while True:
        log("Waiting for chunk")
        msg = socket.recv()

        if msg == 'end':
            best_hypotheses = nbest_hypotheses(n=10)

            socket.send_json({'type': 'result', 'result': create_response(best_hypotheses)})
            socket.send_json({'type': 'end'})
            log('Final hypothesis sent')
            break

        pcm = resample_to_def_sample_rate(msg, 44100, 16000)
        best_hypothesis = recognize_chunk(pcm)
        socket.send_json({'type': 'result', 'result': create_response([best_hypothesis])})
        log("Interim results sent")

