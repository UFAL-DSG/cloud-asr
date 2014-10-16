class SocketSpy:

    def __init__(self):
        self.messages = []
        self.sent_message = None
        self.sent_messages = []
        self.connected_to = None
        self.is_disconnected = None

    def set_messages(self, messages):
        self.messages = messages

    def connect(self, address):
        self.connected_to = address
        self.is_disconnected = False

    def disconnect(self, address):
        if address == self.connected_to:
            self.is_disconnected = True

    def send(self, message):
        self.sent_messages.append(message)
        self.sent_message = message

    def send_json(self, message):
        self.sent_messages.append(message)
        self.sent_message = message

    def recv(self):
        return self.messages.pop(0)

    def recv_json(self):
        return self.messages.pop(0)

    def has_next_message(self):
        return len(self.messages) > 0
