import os
import sys
import wave
import struct
import datetime
from socketIO_client import SocketIO


def create_sockets(server, port, n):
    sockets = []

    for i in range(0, n):
        socket = SocketIO(server, port)
        socket.on('result', print_result(i))
        socket.on('final_result', print_final_result(i))
        socket.on('server_error', print_server_error(i))

        sockets.append(socket)

    return sockets

def print_result(i):
    def print_result_for_socket(result):
        log("Socket %d received result: %s" % (i, result))

    return print_result_for_socket

def print_final_result(i):
    def print_final_result_for_socket(result):
        log("Socket %d received final result: %s" % (i, result))

    return print_final_result_for_socket

def print_server_error(i):
    def print_server_error_for_socket(error):
        log("Socket %d caused server error: %s" % (i, error))

    return print_server_error_for_socket

def run_requests(sockets):
    for socket_id, socket in enumerate(sockets):
        log("Beginning communication via socket %d" % socket_id)
        socket.emit('begin', {'model': 'en-GB'})

    for chunk_id, chunk in enumerate(chunks()):
        for socket_id, socket in enumerate(sockets):
            log("Sending chunk %d via socket %d" % (chunk_id, socket_id))
            socket.emit('chunk', {'chunk': chunk, 'frame_rate': 16000})
            socket.wait_for_callbacks()

    for socket_id, socket in enumerate(sockets):
        log("Ending communication via socket %d" % socket_id)
        socket.emit('end', {})
        socket.wait_for_callbacks()
        socket.wait_for_callbacks()

def chunks():
    basedir = os.path.dirname(os.path.realpath(__file__))
    wav = wave.open("%s/../resources/test.wav" % basedir, "rb")

    while True:
        frames = wav.readframes(4096)
        if len(frames) == 0:
            break

        yield frames_to_pcm_array(frames)

def frames_to_pcm_array(frames):
    return [struct.unpack('h', frames[i:i+2])[0] for i in range(0, len(frames), 2)]

def log(message):
    time = datetime.datetime.now().time()
    print "[%s]\t%s" % (time, message)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "Usage python benchmarks/benchmark_online_recognition.py server port number_of_sockets"
        sys.exit(1)

    server = sys.argv[1]
    port = int(sys.argv[2])
    number_of_sockets = int(sys.argv[3])

    sockets = create_sockets(server, port, number_of_sockets)
    run_requests(sockets)
