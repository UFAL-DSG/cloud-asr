import gevent
from flask import Flask, request, jsonify, render_template
from flask.ext.socketio import SocketIO
from lib import create_recordings_saver, RecordingsModel


app = Flask(__name__)
app.config['DEBUG'] = True
socketio = SocketIO(app)
saver = create_recordings_saver("tcp://0.0.0.0:5682", "/opt/app/static/data")
model = RecordingsModel("/opt/app/static/data")

@app.route('/')
def index():
    return render_template('index.html', recordings=model.get_recordings())

if __name__ == "__main__":
    from gevent import monkey
    monkey.patch_all()

    gevent.spawn(saver.run)
    socketio.run(app, host="0.0.0.0", port=80)
