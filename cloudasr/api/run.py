import os
import sys
import json
from flask import Flask, Response, request, jsonify, stream_with_context
from flask.ext.cors import CORS
from flask.ext.sockets import Sockets
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
sockets = Sockets(app)
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

    worker = None
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
        if worker:
            worker.close()


@app.route("/transcribe", methods=['POST'])
def transcribe():
    try:
        data = request.get_json(force=True)
        user_id = data.get("user_id", None)
        recording_id = data["recording_id"]
        transcription = data["transcription"]

        result = recordings_model.add_transcription(user_id, recording_id, transcription)
        if result is True:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Recording with id %s not found" % str(recording_id)}), 404
    except KeyError as e:
        return jsonify({"status": "error", "message": "Missing item %s" % e.args[0]}), 400

@sockets.route('/transcribe-online')
def trabscribe_online(ws):
    model = ws.receive()
    frame_rate = int(ws.receive())

    worker = None
    try:
        worker = create_frontend_worker(os.environ['MASTER_ADDR'])
        worker.connect_to_worker(model)
        app.logger.info('API connected to worker')

        while not ws.closed:
            chunk = ws.receive()

            if len(chunk) != 0:
                results = worker.recognize_chunk(chunk, frame_rate)
                for result in results:
                    ws.send(json.dumps(result))
            else:
                results = worker.end_recognition()
                for result in results:
                    ws.send(json.dumps(result))
                break
    except NoWorkerAvailableError:
        ws.send({"status": "error", "message": "No worker available"})
    except WorkerInternalError:
        ws.send({"status": "error", "message": "Internal error"})
    finally:
        if worker:
            app.logger.info('Closing connection to worker') 
            worker.close()

if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('0.0.0.0', 80), app, handler_class=WebSocketHandler)
    server.serve_forever()
