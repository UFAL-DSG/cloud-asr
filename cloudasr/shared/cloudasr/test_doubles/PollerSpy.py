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
        if not self.has_next_message():
            return {}, self.time

        timeout = float(timeout)/1000
        next_messages = self.messages[0]

        if "time" in next_messages:
            if next_messages["time"] > timeout:
                self.messages[0]["time"] = self.messages[0]["time"] - timeout
                messages = {}
                self.time += timeout
            else:
                messages = self.messages.pop(0)
                self.time += messages.pop("time")
        else:
            self.time += 1
            messages = self.messages.pop(0)

        return messages, self.time

    def send(self, socket, message):
        self.sent_messages[socket].append(message)


