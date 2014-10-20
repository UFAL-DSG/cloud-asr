import zmq.green as zmq
from cloudasr.messages.helpers import *


def create_monitor(address, emit):
    def create_socket():
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind(address)
        return socket

    run_forever = lambda: True

    return Monitor(create_socket, emit, run_forever)


class Monitor:

    def __init__(self, create_socket, emit, should_continue):
        self.create_socket = create_socket
        self.emit = emit
        self.should_continue = should_continue

    def run(self):
        self.socket = self.create_socket()

        while self.should_continue():
            message = parseWorkerStatusMessage(self.socket.recv())
            self.emit({
                "address": message.address,
                "model": message.model,
                "status": "WAITING" if message.status == 0 else "WORKING",
                "time": message.time
            })
