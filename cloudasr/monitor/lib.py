from cloudasr.messages.helpers import *


class Monitor:

    def __init__(self, socket, emit, should_continue):
        self.socket = socket
        self.emit = emit
        self.should_continue = should_continue

    def run(self):
        while self.should_continue():
            message = parseWorkerStatusMessage(self.socket.recv())
            self.emit({
                "address": message.address,
                "model": message.model,
                "status": "WAITING" if message.status == 0 else "WORKING",
                "time": message.time
            })
