import zmq
import time
from collections import defaultdict


def create_master(worker_address, frontend_address):
    poller = create_poller(worker_address, frontend_address)
    run_forever = lambda: True

    return Master(poller, run_forever)


def create_poller(worker_address, frontend_address):
    context = zmq.Context()
    worker_socket = context.socket(zmq.REP)
    worker_socket.bind(worker_address)
    frontend_socket = context.socket(zmq.REP)
    frontend_socket.bind(frontend_address)

    sockets = {
        "worker": worker_socket,
        "frontend": frontend_socket,
    }
    time_func = time.time

    return Poller(sockets, time_func)


class Master:

    def __init__(self, poller, should_continue):
        self.poller = poller
        self.should_continue = should_continue
        self.workers_status = defaultdict(lambda: {"status": "DEAD", "last_heartbeat": 0})
        self.available_workers = defaultdict(list)
        self.time = 0

    def run(self):
        while self.should_continue():
            messages, self.time = self.poller.poll()

            if "worker" in messages:
                self.handle_worker_request(messages["worker"])

            if "frontend" in messages:
                self.handle_fronted_request(messages["frontend"])

    def handle_fronted_request(self, message):
        model = message["model"]

        worker = self.find_available_worker(model)
        if worker is not None:
            self.update_worker_status(worker, "WORKING")

            message = {
                "status": "success",
                "address": worker
            }

            self.poller.send("frontend", message)
        else:
            message = {
                "status": "error",
                "message": "No worker available"
            }

            self.poller.send("frontend", message)

    def handle_worker_request(self, message):
        model = message["model"]
        address = message["address"]

        if self.workers_status[address]["status"] != "WAITING":
            self.available_workers[model].append(address)
            self.update_worker_status(address, "WAITING")

        self.poller.send("worker", {"status": "success"})

    def find_available_worker(self, model):
        while len(self.available_workers[model]) > 0:
            worker = self.available_workers[model].pop(0)

            if self.is_worker_available(worker):
                return worker

        return None

    def is_worker_available(self, worker):
        status = self.workers_status[worker]
        return status["status"] == "WAITING" and status["last_heartbeat"] > self.time - 10

    def update_worker_status(self, worker, status):
        self.workers_status[worker] = {
            "status": status,
            "last_heartbeat": self.time
        }


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
