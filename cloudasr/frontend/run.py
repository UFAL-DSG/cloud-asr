from flask import Flask, request, jsonify
from lib import create_frontend_worker
import os
app = Flask(__name__)
worker = create_frontend_worker(os.environ['WORKER_ADDR'])


@app.route("/recognize", methods=['POST'])
def recognize_batch():
    return jsonify(worker.recognize_batch(request.data))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
