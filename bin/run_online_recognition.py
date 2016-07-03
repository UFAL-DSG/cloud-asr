import sys
import wave
import json
import base64
import datetime
from websocket import create_connection


def create_socket(server, port):
    return create_connection("ws://%s:%d/transcribe-online" % (server, port))

def handle_response(response):
    response = json.loads(response)

    if response["status"] == "error":
        print_server_error(response)
    else:
        print_result(response)

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

        yield frames

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
    frame_rate = sys.argv[5]

    socket = create_socket(server, port)
    socket.send(model)
    socket.send(frame_rate)
    for chunk in chunks(path):
        socket.send_binary(chunk)
        handle_response(socket.recv())

    socket.send_binary("")
    handle_response(socket.recv())
