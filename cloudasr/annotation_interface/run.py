import os
import gevent
from flask import Flask
from flask.ext.socketio import SocketIO
from lib import create_recordings_saver, create_db_connection, RecordingsModel


app = Flask(__name__)
app.config.update(
    SECRET_KEY = '12345',
    DEBUG = True,
)
socketio = SocketIO(app)

db = create_db_connection(os.environ['CONNECTION_STRING'])
recordings_model = RecordingsModel(db, os.environ['STORAGE_PATH'], os.environ['DOMAIN'])
saver = create_recordings_saver("tcp://0.0.0.0:5682", recordings_model)

if __name__ == "__main__":
    from gevent import monkey
    monkey.patch_all()

    gevent.spawn(saver.run)
    socketio.run(app, host="0.0.0.0", port=80)
