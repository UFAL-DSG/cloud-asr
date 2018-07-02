import os
import json
from flask import Flask, Response, request, jsonify, stream_with_context, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
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
        "lm": request.args.get("lm", "default"),
        "wav": request.data
    }

    def generate(response):
        for result in response:
            yield json.dumps(result)

    try:
        worker = create_frontend_worker(os.environ['MASTER_ADDR'])
        response = worker.recognize_batch(data, request.headers)
        worker.close()

        return Response(stream_with_context(generate(response)))
    except MissingHeaderError:
        return jsonify({"status": "error", "message": "Missing header Content-Type"}), 400
    except NoWorkerAvailableError:
        return jsonify({"status": "error", "message": "No worker available"}), 503
    finally:
        worker.close()


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
        session["connected"] = True
    except NoWorkerAvailableError:
        emit('server_error', {"status": "error", "message": "No worker available"})
        worker.close()

@socketio.on('chunk')
def recognize_chunk(message):
    try:
        if not session.get("connected", False):
            emit('server_error', {"status": "error", "message": "No worker available"})
            return

        results = session["worker"].recognize_chunk(message["chunk"], message["frame_rate"])
        for result in results:
            emit('result', result)
    except WorkerInternalError:
        emit('server_error', {"status": "error", "message": "Internal error"})
        session["worker"].close()
        del session["worker"]

@socketio.on('change_lm')
def change_lm(message):
    try:
        if not session.get("connected", False):
            emit('server_error', {"status": "error", "message": "No worker available"})
            return

        results = session["worker"].change_lm(str(message["new_lm"]))
        for result in results:
            emit('result', result)
    except WorkerInternalError:
        emit('server_error', {"status": "error", "message": "Internal error"})
        session["worker"].close()
        del session["worker"]

@socketio.on('end')
def end_recognition(message):
    if not session.get("connected", False):
        emit('server_error', {"status": "error", "message": "No worker available"})
        return

    results = session["worker"].end_recognition()
    for result in results:
        emit('result', result)

    emit('end', results[-1])

    session["worker"].close()
    session["connected"] = False
    del session["worker"]

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=80)
