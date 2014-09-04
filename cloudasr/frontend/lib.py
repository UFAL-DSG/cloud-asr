import zmq

def create_frontend_worker(background_worker_address):
    context = zmq.Context()
    background_worker_socket = context.socket(zmq.REQ)
    background_worker_socket.connect(background_worker_address)

    return FrontendWorker(background_worker_socket)


class FrontendWorker:
    def __init__(self, worker_socket):
        self.worker_socket = worker_socket

    def recognize_batch(self, data):
        self.worker_socket.send(data)
        return self.worker_socket.recv_json()
