import zmq


def create_worker(worker_address):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(worker_address)

    asr = ASR()
    run_forever = lambda: True

    return Worker(socket, asr, run_forever)


class Worker:

    def __init__(self, socket, asr, should_continue):
        self.socket = socket
        self.asr = asr
        self.should_continue = should_continue

    def run(self):
        while self.should_continue():
            message = self.socket.recv()
            self.asr.recognize_chunk(message)
            final_hypothesis = self.asr.get_final_hypothesis()
            self.socket.send_json(final_hypothesis)


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
