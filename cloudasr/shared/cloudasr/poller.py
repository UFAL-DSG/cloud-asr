import zmq.green as zmq

class Poller:

    def __init__(self, sockets, time):
        self.sockets = sockets
        self.poller = zmq.Poller()

        for socket in self.sockets.values():
            self.poller.register(socket["socket"], zmq.POLLIN | zmq.POLLOUT)

        self.time = time

    def poll(self, timeout=1000):
        sockets = dict(self.poller.poll(timeout))

        messages = {}
        for name, socket in self.sockets.iteritems():
            if self.has_received_message(socket, sockets):
                messages[name] = socket["receive"]()

        return messages, self.time()

    def has_received_message(self, socket, sockets):
        return socket["socket"] in sockets and sockets[socket["socket"]] == zmq.POLLIN

    def send(self, socket, message):
        self.sockets[socket]["send"](message)
