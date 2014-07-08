import os
import sys
import wave
import struct
from socketIO_client import SocketIO

def frames_to_pcm_array(frames):
    return [struct.unpack('h', frames[i:i+2])[0] for i in range(0, len(frames), 2)]

def chunks(wav):
    while True:
        frames = wav.readframes(16384)
        if len(frames) == 0:
            break

        yield frames_to_pcm_array(frames)

def print_response(*args):
    print "result: ", args

def end(*args):
    sys.exit(1)


basedir = os.path.dirname(os.path.realpath(__file__))
wav = wave.open('%s/../resources/test.wav' % basedir, 'rb')

with SocketIO('192.168.10.10', 80) as socketIO:
    socketIO.on('result', print_response)
    socketIO.on('end', end)

    socketIO.emit('begin', {'lang': 'cs'})
    for chunk in chunks(wav):
        socketIO.emit('chunk', {'chunk': chunk})
    socketIO.emit('end', {})

    socketIO.wait()


