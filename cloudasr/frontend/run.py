from flask import Flask, request, jsonify
from lib import create_frontend_worker
import os
app = Flask(__name__)
worker = create_frontend_worker(os.environ['MASTER_ADDR'])


@app.route("/recognize", methods=['POST'])
def recognize_batch():
    data = {
        "model": "en-GB",
        "wav": request.data
    }

    return jsonify(worker.recognize_batch(data))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
