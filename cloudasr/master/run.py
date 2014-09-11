import zmq
import os

context = zmq.Context()
worker_socket = context.socket(zmq.REP)
worker_socket.bind(os.environ['WORKER_ADDR'])

while True:
    msg = worker_socket.recv()
    worker_socket.send("OK")
    print msg

