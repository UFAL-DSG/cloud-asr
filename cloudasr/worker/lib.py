import zmq


def create_worker(model, worker_socket_address, worker_public_address, master_address):
    context = zmq.Context()
    worker_socket = context.socket(zmq.REP)
    worker_socket.bind(worker_socket_address)
    master_socket = context.socket(zmq.REQ)
    master_socket.connect(master_address)

    asr = ASR()
    run_forever = lambda: True

    return Worker(model, worker_public_address, worker_socket, master_socket, asr, run_forever)


class Worker:

    def __init__(self, model, my_address, my_socket, master_socket, asr, should_continue):
        self.model = model
        self.my_address = my_address
        self.my_socket = my_socket
        self.master_socket = master_socket
        self.asr = asr
        self.should_continue = should_continue

    def run(self):
        while self.should_continue():
            self.send_heartbeat()

            message = self.my_socket.recv()
            self.asr.recognize_chunk(message)
            final_hypothesis = self.asr.get_final_hypothesis()
            response = self.create_response(final_hypothesis)
            self.my_socket.send_json(response)

    def send_heartbeat(self):
        message = {
            "address": self.my_address,
            "model": self.model
        }

        self.master_socket.send_json(message)
        self.master_socket.recv()

    def create_response(self, final_hypothesis):
        return {
            "result": [
                {
                    "alternative": [{"confidence": c, "transcript": t} for (c,t) in final_hypothesis],
                    "final": True,
                },
            ],
            "result_index": 0,
        }


class ASR:

    def recognize_chunk(self, chunk):
        pass

    def get_final_hypothesis(self):
        return [(1.0, "Hello World!")]
