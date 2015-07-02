import zmq
import time
from collections import defaultdict
from cloudasr import Poller
from cloudasr.messages import HeartbeatMessage
from cloudasr.messages.helpers import *


def create_master(worker_address, frontend_address, monitor_address):
    poller = create_poller(worker_address, frontend_address)
    context = zmq.Context()
    monitor = context.socket(zmq.PUSH)
    monitor.connect(monitor_address)
    run_forever = lambda: True

    return Master(poller, monitor, run_forever)


def create_poller(worker_address, frontend_address):
    context = zmq.Context()
    worker_socket = context.socket(zmq.PULL)
    worker_socket.bind(worker_address)
    frontend_socket = context.socket(zmq.REP)
    frontend_socket.bind(frontend_address)

    sockets = {
        "worker": {"socket": worker_socket, "receive": worker_socket.recv, "send": worker_socket.send_json},
        "frontend": {"socket": frontend_socket, "receive": frontend_socket.recv, "send": frontend_socket.send},
    }
    time_func = time.time

    return Poller(sockets, time_func)


class Master:

    def __init__(self, poller, monitor, should_continue):
        self.poller = poller
        self.should_continue = should_continue
        self.workers = WorkerPool(monitor)
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
            request = parseWorkerRequestMessage(message)
            model = request.model
            worker = self.workers.get_worker(model, self.time)

            message = createMasterResponseMessage("SUCCESS", worker)
            self.poller.send("frontend", message.SerializeToString())
        except NoWorkerAvailableException:
            message = createMasterResponseMessage("ERROR")
            self.poller.send("frontend", message.SerializeToString())

    def handle_worker_request(self, message):
        statuses = {
            HeartbeatMessage.STARTED: "STARTED",
            HeartbeatMessage.WAITING: "WAITING",
            HeartbeatMessage.WORKING: "WORKING",
            HeartbeatMessage.FINISHED: "FINISHED"
        }

        heartbeat = parseHeartbeatMessage(message)
        address = heartbeat.address
        model = heartbeat.model
        status = statuses[heartbeat.status]

        self.workers.add_worker(model, address, status, self.time)


class WorkerPool:

    def __init__(self, monitor):
        self.workers_status = defaultdict(lambda: {"status": "STARTED", "last_heartbeat": 0, "waiting_for_first_chunk_secs": 0})
        self.available_workers = defaultdict(list)
        self.monitor = monitor

    def get_worker(self, model, time):
        worker = self.find_available_worker(model, time)

        if worker is None:
            raise NoWorkerAvailableException()

        self.update_worker_status(model, worker, "WORKING", time)
        return worker

    def find_available_worker(self, model, time):
        while len(self.available_workers[model]) > 0:
            worker = self.available_workers[model].pop(0)

            if self.is_worker_available(worker, time):
                return worker

        return None

    def is_worker_available(self, worker, time):
        status = self.workers_status[worker]
        return status["status"] and status["last_heartbeat"] > time - 10

    def add_worker(self, model, address, status, time):
        worker_status = self.workers_status[address]["status"]
        if worker_status == "WORKING":
            if status == "FINISHED" or status == "STARTED":
                self.available_workers[model].append(address)
                self.update_worker_status(model, address, "WAITING", time)

            if status == "WORKING":
                self.update_worker_status(model, address, "WORKING", time)

            if status == "WAITING":
                self.workers_status[address]["waiting_for_first_chunk_secs"] += 1

                if self.workers_status[address]["waiting_for_first_chunk_secs"] == 10:
                    self.available_workers[model].append(address)
                    self.update_worker_status(model, address, "WAITING", time)
        elif worker_status == "STARTED":
            self.available_workers[model].append(address)
            self.update_worker_status(model, address, "STARTED", time)
        elif worker_status == "WAITING":
            self.update_worker_status(model, address, "WAITING", time)

    def update_worker_status(self, model, worker, status, time):
        self.workers_status[worker] = {
            "status": "WAITING" if status == "STARTED" else status,
            "last_heartbeat": time,
            "waiting_for_first_chunk_secs": 0
        }

        worker_status = createWorkerStatusMessage(worker, model, status, int(time))
        self.monitor.send(worker_status.SerializeToString())


class NoWorkerAvailableException(Exception):
    pass
