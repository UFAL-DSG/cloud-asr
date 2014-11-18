import zmq.green as zmq
from cloudasr.messages.helpers import *


def create_monitor(address, socketio):
    def create_socket():
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind(address)
        return socket

    def emit(message):
        socketio.emit("status_update", message)

    run_forever = lambda: True

    return Monitor(create_socket, emit, run_forever)


class Monitor:

    def __init__(self, create_socket, emit, should_continue):
        self.create_socket = create_socket
        self.emit = emit
        self.statuses = {}
        self.should_continue = should_continue

    def get_statuses(self):
        return self.statuses.values()

    def run(self):
        self.socket = self.create_socket()

        while self.should_continue():
            message = parseWorkerStatusMessage(self.socket.recv())
            status = {
                "address": message.address,
                "model": message.model,
                "status": "WAITING" if message.status == 0 else "WORKING",
                "time": message.time
            }

            self.statuses[message.address] = status
            self.emit(status)
