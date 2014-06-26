import zmq

def recognize_wav(data):
    port = 5559
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:%s" % port)
    socket.send(data)

    return socket.recv_json()
