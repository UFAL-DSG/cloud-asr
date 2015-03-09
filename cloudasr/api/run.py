from flask import Flask, Response, request, jsonify, stream_with_context
from flask.ext.socketio import SocketIO, emit, session
from lib import create_frontend_worker, MissingHeaderError, NoWorkerAvailableError, WorkerInternalError
import os
import json
app = Flask(__name__)
app.secret_key = "12345"
app.config['DEBUG'] = True
socketio = SocketIO(app)


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
