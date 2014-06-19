from flask import Flask, render_template, request, jsonify
from asr import recognize_wav

app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/recognize', methods=['POST'])
def recognize():
    return jsonify(recognize_wav(request.data))


if __name__ == '__main__':
    app.run(debug=True)
