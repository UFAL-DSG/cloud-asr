from collections import defaultdict


class PollerSpy:

    def __init__(self):
        self.messages = []
        self.sent_messages = defaultdict(list)
        self.time = 0

    def add_messages(self, messages):
        self.messages.extend(messages)

    def has_next_message(self):
        return len(self.messages) > 0

    def poll(self, timeout=1000):
        timeout = float(timeout)/1000
        messages = self.messages.pop(0)
        if "time" in messages:
            self.time += messages.pop("time")
        else:
            self.time += 1

        return messages, self.time

    def send(self, socket, message):
        self.sent_messages[socket].append(message)


