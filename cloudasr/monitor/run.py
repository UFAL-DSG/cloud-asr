from flask import Flask, request, jsonify, render_template, copy_current_request_context
from flask.ext.socketio import SocketIO, emit, session
import gevent
from lib import create_monitor
import os
app = Flask(__name__)
app.config['DEBUG'] = True
socketio = SocketIO(app)
monitor = create_monitor(os.environ["MONITOR_ADDR"], socketio)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/statuses')
def statuses():
    return jsonify({"statuses": monitor.get_statuses()})

@app.route('/available-workers')
def available_workers():
    return jsonify(monitor.get_available_workers_per_model())

@socketio.on("stream_statuses")
def start(message):
    pass

if __name__ == "__main__":
    from gevent import monkey
    monkey.patch_all()

    gevent.spawn(monitor.run)
    socketio.run(app, host="0.0.0.0", port=80)
