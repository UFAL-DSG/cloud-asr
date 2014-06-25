from flask import Flask, render_template, request, jsonify
from asr import recognize_wav, asr_init
import os

basedir = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/recognize', methods=['POST'])
def recognize():
    return jsonify(recognize_wav(request.data))


if __name__ == '__main__':
    asr_init(basedir)

    app.run(debug=True)
