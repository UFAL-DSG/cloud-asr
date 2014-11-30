import time
import zmq.green as zmq
from cloudasr import Poller
from cloudasr.messages.helpers import *


def create_monitor(address, socketio):
    def create_poller():
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind(address)

        sockets = {
            "master": {"socket": socket, "receive": socket.recv, "send": socket.send},
        }
        time_func = time.time

        return Poller(sockets, time_func)

    def emit(message):
        socketio.emit("status_update", message)

    run_forever = lambda: True

    return Monitor(create_poller, emit, run_forever)


class Monitor:

    def __init__(self, create_poller, emit, should_continue):
        self.create_poller = create_poller
        self.emit = emit
        self.statuses = {}
        self.should_continue = should_continue

    def get_statuses(self):
        return self.statuses.values()

    def run(self):
        self.poller = self.create_poller()

        while self.should_continue():
            messages, time = self.poller.poll(1000)

            if "master" in messages:
                self.handle_message(messages["master"])

    def handle_message(self, message):
        message = parseWorkerStatusMessage(message)
        status = {
            "address": message.address,
            "model": message.model,
            "status": "WAITING" if message.status == 0 else "WORKING",
            "time": message.time
        }

        self.statuses[message.address] = status
        self.emit(status)
