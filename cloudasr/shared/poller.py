import zmq

class Poller:

    def __init__(self, sockets, time):
        self.sockets = sockets
        self.poller = zmq.Poller()

        for socket in self.sockets.values():
            self.poller.register(socket, zmq.POLLIN | zmq.POLLOUT)

        self.time = time

    def poll(self, timeout=1000):
        socks = dict(self.poller.poll(timeout))

        messages = {}
        for name, socket in self.sockets.iteritems():
            if socket in socks and socks[socket] == zmq.POLLIN:
                print "Received message on %s" % name
                messages[name] = socket.recv_json()

        return messages, self.time()

    def send(self, socket, message):
        self.sockets[socket].send_json(message)
