import sys
import wave
import base64
import datetime
from socketIO_client import SocketIO


def create_socket(server, port):
    socket = SocketIO(server, port)
    socket.on('result', print_result)
    socket.on('server_error', print_server_error)

    return socket

def print_result(result):
    if result["final"]:
        log(result["result"]["hypotheses"][0])

def print_server_error(error):
    log(error)

def chunks(path):
    wav = wave.open(path, "rb")

    while True:
        frames = wav.readframes(16384)
        if len(frames) == 0:
            break

        yield frames_to_base64(frames)

def frames_to_base64(frames):
    return base64.b64encode(frames)

def log(message):
    time = datetime.datetime.now().time()
    print "[%s]\t%s" % (time, message)


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print "Usage python run_online_recognition.py server port file model frame_rate"
        sys.exit(1)

    server = sys.argv[1]
    port = int(sys.argv[2])
    path = sys.argv[3]
    model = sys.argv[4]
    frame_rate = int(sys.argv[5])

    socket = create_socket(server, port)
    socket.emit('begin', {'model': model})
    for chunk in chunks(path):
        socket.emit('chunk', {'chunk': chunk, 'frame_rate': frame_rate})
        socket.wait_for_callbacks()
    socket.emit('end', {})
    socket.wait_for_callbacks()
    socket.wait_for_callbacks()
