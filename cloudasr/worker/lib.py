import zmq


def create_worker(worker_address, master_address):
    context = zmq.Context()
    worker_socket = context.socket(zmq.REP)
    worker_socket.bind(worker_address)
    master_socket = context.socket(zmq.REQ)
    master_socket.connect(master_address)

    asr = ASR()
    run_forever = lambda: True

    return Worker(worker_address, worker_socket, master_socket, asr, run_forever)


class Worker:

    def __init__(self, my_address, my_socket, master_socket, asr, should_continue):
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
            self.my_socket.send_json(final_hypothesis)

    def send_heartbeat(self):
        self.master_socket.send(self.my_address)
        self.master_socket.recv()

class ASR:

    def recognize_chunk(self, chunk):
        pass

    def get_final_hypothesis(self):
        return {
            "result": [
                {
                    "alternative": [
                        {
                            "confidence": 1.0,
                            "transcript": "Hello World!"
                        },
                    ],
                    "final": True,
                },
            ],
            "result_index": 0,
        }
