import time
import zmq.green as zmq
from cloudasr import Poller
from cloudasr.messages.helpers import *
from collections import defaultdict


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

    scale_workers = lambda command: True
    run_forever = lambda: True

    return Monitor(create_poller, emit, scale_workers, run_forever)


class Monitor:

    def __init__(self, create_poller, emit, scale_workers, should_continue):
        self.create_poller = create_poller
        self.emit = emit
        self.scale_workers_callback = scale_workers
        self.should_continue = should_continue
        self.statuses = {}
        self.scaling = {}

    def get_statuses(self):
        return self.statuses.values()

    def get_available_workers_per_model(self):
        (availableWorkersPerModel, newWorkersPerModel) = self.count_workers_per_model()
        return availableWorkersPerModel

    def run(self):
        self.poller = self.create_poller()

        while self.should_continue():
            messages, time = self.poller.poll(1000)

            if "master" in messages:
                self.handle_message(messages["master"])

            self.scale_workers(time)

    def scale_workers(self, time):
        (availableWorkersPerModel, newWorkersPerModel) = self.count_workers_per_model()
        command = self.create_scaling_command(availableWorkersPerModel, newWorkersPerModel)
        self.scale_workers_callback(command)

    def count_workers_per_model(self):
        availableWorkersPerModel = defaultdict(int)
        newWorkersPerModel = defaultdict(int)

        for worker in self.statuses.itervalues():
            availableWorkersPerModel[worker["model"]] += 0 if worker["status"] == "WORKING" else 1
            newWorkersPerModel[worker["model"]] += 1 if worker["status"] == "STARTED" else 0

        return (availableWorkersPerModel, newWorkersPerModel)

    def create_scaling_command(self, availableWorkersPerModel, newWorkersPerModel):
        command = {}
        for model in availableWorkersPerModel:
            availableWorkers = availableWorkersPerModel[model]
            newWorkers = newWorkersPerModel[model]

            if model not in self.scaling and availableWorkers == 0:
                self.scaling[model] = True
                command[model] = 1

            if model in self.scaling and newWorkers != 0:
                del self.scaling[model]

        return command

    def handle_message(self, message):
        message = parseWorkerStatusMessage(message)
        statuses = {
            0: "STARTED",
            1: "WAITING",
            2: "WORKING"
        }

        status = {
            "address": message.address,
            "model": message.model,
            "status": statuses[message.status],
            "time": message.time
        }

        self.statuses[message.address] = status
        self.emit(status)
