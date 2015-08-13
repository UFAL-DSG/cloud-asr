import os
import sys
import wave
import base64
import random
import struct
import datetime
from socketIO_client import SocketIO


def create_sockets(server, port, n):
    sockets = []

    for i in range(0, n):
        socket = SocketIO(server, port)
        socket.on('result', print_result(i))
        socket.on('server_error', print_server_error(i))

        sockets.append(socket)

    return sockets

def print_result(i):
    def print_result_for_socket(result):
        log("Socket %d received result: %s" % (i, result))

    return print_result_for_socket

def print_server_error(i):
    def print_server_error_for_socket(error):
        log("Socket %d caused server error: %s" % (i, error))

    return print_server_error_for_socket

def generate_schedule(sockets):
    wave_chunks = list(chunks())

    schedules = []
    for socket_id, socket in enumerate(sockets):
        schedule = []
        schedule.append(begin(socket_id, socket))
        for chunk_id, chunk in enumerate(wave_chunks):
                schedule.append(send_chunk(socket_id, socket, chunk_id, chunk))
                schedule.append(wait_for_reply(socket_id, socket))

        schedule.append(end(socket_id, socket))
        schedule.append(wait_for_reply(socket_id, socket))
        schedule.append(wait_for_reply(socket_id, socket))

        schedules.append(schedule)

    return schedules

def chunks():
    basedir = os.path.dirname(os.path.realpath(__file__))
    wav = wave.open("%s/../resources/test.wav" % basedir, "rb")

    while True:
        frames = wav.readframes(16384)
        if len(frames) == 0:
            break

        yield frames_to_base64(frames)

def frames_to_base64(frames):
    return base64.b64encode(frames)

def begin(socket_id, socket):
    def callback():
        log("Beginning communication via socket %d" % socket_id)
        socket.emit('begin', {'model': 'en-towninfo'})

    return callback

def send_chunk(socket_id, socket, chunk_id, chunk):
    def callback():
        log("Sending chunk %d via socket %d" % (chunk_id, socket_id))
        socket.emit('chunk', {'chunk': chunk, 'frame_rate': 16000})

    return callback

def wait_for_reply(socket_id, socket):
    def callback():
        log("Waiting for reply via socket %d" % socket_id)
        socket.wait_for_callbacks()

    return callback

def end(socket_id, socket):
    def callback():
        log("Ending communication via socket %d" % socket_id)
        socket.emit('end', {})

    return callback

def run_random_schedule(schedules):
    for action in random_schedule(schedules):
        action()

def random_schedule(schedules):
    order = []
    for i, schedule in enumerate(schedules):
        order.extend([i] * len(schedule))

    random.shuffle(order)

    for item in order:
        yield schedules[item].pop(0)

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
    schedules = generate_schedule(sockets)
    run_random_schedule(schedules)
