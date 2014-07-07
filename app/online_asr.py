import zmq
import struct

class OnlineASR:
    def __init__(self, emit):
        port = "5660"
        context = zmq.Context()
        socket = context.socket(zmq.PAIR)
        socket.connect("tcp://localhost:%s" % port)
        print "Socket created"

        self.socket = socket
        self.emit = emit

    def recognize_chunk(self, message):
        print "PCM received"
        pcm = b''.join([struct.pack('h', i) for i in message['chunk']])

        print self.socket.send(pcm)

        print "Waiting for result"
        msg = self.socket.recv_json()

        print "Sending interim result"
        self.emit('result', msg['result'])

    def end(self):
        self.socket.send("end")
        print "Ending socket"

        while True:
            msg = self.socket.recv_json()

            if msg['type'] == 'end':
                self.emit('end', {})
                self.socket.close()
                break

            self.emit('result', msg['result'])
