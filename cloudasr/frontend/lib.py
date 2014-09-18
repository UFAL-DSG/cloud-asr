import zmq

def create_frontend_worker(master_address):
    context = zmq.Context()
    master_socket = context.socket(zmq.REQ)
    master_socket.connect(master_address)
    worker_socket = context.socket(zmq.REQ)

    return FrontendWorker(master_socket, worker_socket)


class FrontendWorker:
    def __init__(self, master_socket, worker_socket):
        self.master_socket = master_socket
        self.worker_socket = worker_socket

    def recognize_batch(self, data):
        worker_address = self.get_worker_address_from_master(data["model"])
        response = self.recognize_batch_on_worker(worker_address, data)

        return response

    def get_worker_address_from_master(self, model):
        self.master_socket.send_json({"model": model})
        response = self.master_socket.recv_json()

        if response["status"] == "success":
            return response["address"]
        else:
            raise NoWorkerAvailableError()

    def recognize_batch_on_worker(self, worker_address, data):
        self.worker_socket.connect(worker_address)
        self.worker_socket.send(data["wav"])
        response = self.worker_socket.recv_json()
        self.worker_socket.disconnect(worker_address)

        return response


class NoWorkerAvailableError(Exception):
    pass
