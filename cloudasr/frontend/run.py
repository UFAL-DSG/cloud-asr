from flask import Flask, request, jsonify, render_template
from flask.ext.socketio import SocketIO, emit, session
from lib import create_frontend_worker, MissingHeaderError, NoWorkerAvailableError
import os
app = Flask(__name__)
app.secret_key = 12345
app.config['DEBUG'] = True
socketio = SocketIO(app)
worker = create_frontend_worker(os.environ['MASTER_ADDR'])


@app.route('/')
def index():
    return render_template('index.html')

@app.route("/recognize", methods=['POST'])
def recognize_batch():
    data = {
        "model": "en-GB",
        "wav": request.data
    }

    try:
        return jsonify(worker.recognize_batch(data, request.headers))
    except MissingHeaderError:
        return jsonify({"status": "error", "message": "Missing header Content-Type"}), 400
    except NoWorkerAvailableError:
        return jsonify({"status": "error", "message": "No worker available"}), 503

@socketio.on('begin')
def begin_online_recognition(message):
    try:
        session["worker"] = create_frontend_worker(os.environ['MASTER_ADDR'])
        session["worker"].connect_to_worker(message["model"])
    except NoWorkerAvailableError:
        emit('server_error', {"status": "error", "message": "No worker available"})

@socketio.on('chunk')
def recognize_chunk(message):
    response = session["worker"].recognize_chunk(message["chunk"], message["frame_rate"])
    emit('result', response)

@socketio.on('end')
def end_recognition(message):
    response = session["worker"].end_recognition()
    emit('final_result', response)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8000)
