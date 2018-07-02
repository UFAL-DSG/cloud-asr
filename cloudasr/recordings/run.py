import os
import gevent
from flask import Flask
from flask_socketio import SocketIO
from lib import create_recordings_saver
from cloudasr.schema import db
from cloudasr.models import WorkerTypesModel, RecordingsModel


app = Flask(__name__)
app.config.update(
    SECRET_KEY = '12345',
    DEBUG = True,
    SQLALCHEMY_DATABASE_URI = os.environ['CONNECTION_STRING']
)
socketio = SocketIO(app)

db.init_app(app)
with app.app_context():
    db_session = db.create_session({})

worker_types_model = WorkerTypesModel(db_session)
recordings_model = RecordingsModel(db_session, worker_types_model, os.environ['STORAGE_PATH'], os.environ['DOMAIN'])
saver = create_recordings_saver("tcp://0.0.0.0:5682", recordings_model)

if __name__ == "__main__":
    from gevent import monkey
    monkey.patch_all()

    gevent.spawn(saver.run)
    socketio.run(app, host="0.0.0.0", port=80)
