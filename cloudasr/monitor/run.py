from flask import Flask, request, jsonify, render_template, copy_current_request_context
from flask.ext.socketio import SocketIO, emit, session
import gevent
from lib import create_monitor
import os
app = Flask(__name__)
app.config['DEBUG'] = True
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')

def callback(message):
    socketio.emit("status_update", message)

@socketio.on("stream_statuses")
def start(message):
    pass

if __name__ == "__main__":
    monitor = create_monitor(os.environ["MONITOR_ADDR"], callback)
    gevent.spawn(monitor.run)

    socketio.run(app, host="0.0.0.0", port=8001)
