import unittest
from lib import create_monitor, Monitor
from flask import Flask
from flask.ext.socketio import SocketIO

class TestFactory(unittest.TestCase):

    def test_can_create_monitor(self):
        socketio = self.create_socketio()
        monitor = create_monitor("ipc:///tmp/worker", socketio)
        self.assertIsInstance(monitor, Monitor)

    def create_socketio(self):
        app = Flask(__name__)
        app.config['DEBUG'] = True
        return SocketIO(app)
