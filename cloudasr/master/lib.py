import time
from collections import defaultdict
from cloudasr.messages import HeartbeatMessage, WorkerRequestMessage


def create_master(worker_address, frontend_address):
    poller = create_poller(worker_address, frontend_address)
    run_forever = lambda: True

    return Master(poller, run_forever)


def create_poller(worker_address, frontend_address):
    import zmq
    from cloudasr import Poller
    context = zmq.Context()
    worker_socket = context.socket(zmq.PULL)
    worker_socket.bind(worker_address)
    frontend_socket = context.socket(zmq.REP)
    frontend_socket.bind(frontend_address)

    sockets = {
        "worker": {"socket": worker_socket, "receive": worker_socket.recv},
        "frontend": {"socket": frontend_socket, "receive": frontend_socket.recv},
    }
    time_func = time.time

    return Poller(sockets, time_func)


class Master:

    def __init__(self, poller, should_continue):
        self.poller = poller
        self.should_continue = should_continue
        self.workers = WorkerPool()
        self.time = 0

    def run(self):
        while self.should_continue():
            messages, self.time = self.poller.poll()

            if "worker" in messages:
                self.handle_worker_request(messages["worker"])

            if "frontend" in messages:
                self.handle_fronted_request(messages["frontend"])

    def handle_fronted_request(self, message):
        try:
            request = WorkerRequestMessage()
            request.ParseFromString(message)

            model = request.model
            worker = self.workers.get_worker(model, self.time)

            message = {
                "status": "success",
                "address": worker
            }

            self.poller.send("frontend", message)
        except NoWorkerAvailableException:
            message = {
                "status": "error",
                "message": "No worker available"
            }

            self.poller.send("frontend", message)

    def handle_worker_request(self, message):
        heartbeat = HeartbeatMessage()
        heartbeat.ParseFromString(message)

        address = heartbeat.address
        model = heartbeat.model
        status = "READY" if heartbeat.status == HeartbeatMessage.READY else "FINISHED"

        self.workers.add_worker(model, address, status, self.time)


class WorkerPool:

    def __init__(self):
        self.workers_status = defaultdict(lambda: {"status": "READY", "last_heartbeat": 0})
        self.available_workers = defaultdict(list)

    def get_worker(self, model, time):
        worker = self.find_available_worker(model, time)

        if worker is None:
            raise NoWorkerAvailableException()

        self.update_worker_status(worker, "WORKING", time)
        return worker

    def find_available_worker(self, model, time):
        while len(self.available_workers[model]) > 0:
            worker = self.available_workers[model].pop(0)

            if self.is_worker_available(worker, time):
                return worker

        return None

    def is_worker_available(self, worker, time):
        status = self.workers_status[worker]
        return status["status"] == "WAITING" and status["last_heartbeat"] > time - 10

    def add_worker(self, model, address, status, time):
        if self.workers_status[address]["status"] == "WORKING":
            next_state = "READY" if status == "FINISHED" else "WORKING"
            self.update_worker_status(address, next_state, time)
        elif self.workers_status[address]["status"] == "READY":
            self.available_workers[model].append(address)
            self.update_worker_status(address, "WAITING", time)
        elif self.workers_status[address]["status"] == "WAITING":
            self.update_worker_status(address, "WAITING", time)

    def update_worker_status(self, worker, status, time):
        self.workers_status[worker] = {
            "status": status,
            "last_heartbeat": time
        }

class NoWorkerAvailableException(Exception):
    pass
