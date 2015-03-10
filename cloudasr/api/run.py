import os
import json
from flask import Flask, Response, request, jsonify, stream_with_context
from flask.ext.cors import CORS
from flask.ext.socketio import SocketIO, emit, session
from lib import create_frontend_worker, MissingHeaderError, NoWorkerAvailableError, WorkerInternalError
from cloudasr.schema import db
from cloudasr.models import UsersModel, RecordingsModel, WorkerTypesModel


app = Flask(__name__)
app.config.update(
    SECRET_KEY = '12345',
    DEBUG = 'DEBUG' in os.environ,
    SQLALCHEMY_DATABASE_URI = os.environ['CONNECTION_STRING']
)
cors = CORS(app)
socketio = SocketIO(app)
db.init_app(app)
worker_types_model = WorkerTypesModel(db.session)
recordings_model = RecordingsModel(db.session, worker_types_model)

@app.route("/recognize", methods=['POST'])
def recognize_batch():
    data = {
        "model": request.args.get("lang", "en-GB"),
        "wav": request.data
    }

    def generate(master_addr, data, headers):
        worker = create_frontend_worker(master_addr)
        response = worker.recognize_batch(data, headers)

        for result in response:
            yield json.dumps(result)

    try:
        generator = generate(os.environ['MASTER_ADDR'], data, request.headers)

        return Response(stream_with_context(generator))
    except MissingHeaderError:
        return jsonify({"status": "error", "message": "Missing header Content-Type"}), 400
    except NoWorkerAvailableError:
        return jsonify({"status": "error", "message": "No worker available"}), 503


@app.route("/transcribe", methods=['POST'])
def transcribe():
    try:
        data = request.get_json(force=True)
        user_id = data.get("user_id", None)
        recording_id = data["recording_id"]
        transcription = data["transcription"]

        result = recordings_model.add_transcription(user_id, recording_id, transcription)
        if result == True:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Recording with id %s not found" % str(recording_id)}), 404
    except KeyError as e:
        return jsonify({"status": "error", "message": "Missing item %s" % e.args[0]}), 400

@socketio.on('begin')
def begin_online_recognition(message):
    try:
        worker = create_frontend_worker(os.environ['MASTER_ADDR'])
        worker.connect_to_worker(message["model"])

        session["worker"] = worker
    except NoWorkerAvailableError:
        emit('server_error', {"status": "error", "message": "No worker available"})

@socketio.on('chunk')
def recognize_chunk(message):
    try:
        if "worker" not in session:
            emit('server_error', {"status": "error", "message": "No worker available"})
            return

        results = session["worker"].recognize_chunk(message["chunk"], message["frame_rate"])
        for result in results:
            emit('result', result)
    except WorkerInternalError:
        emit('server_error', {"status": "error", "message": "Internal error"})
        del session["worker"]

@socketio.on('end')
def end_recognition(message):
    if "worker" not in session:
        emit('server_error', {"status": "error", "message": "No worker available"})
        return

    results = session["worker"].end_recognition()
    for result in results:
        emit('result', result)
    del session["worker"]

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=80)
