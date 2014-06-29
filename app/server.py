from flask import Flask, render_template, request, jsonify
from flask.ext.socketio import SocketIO, emit, session
from background_asr import recognize_wav
from online_asr import OnlineASR

app = Flask(__name__)
app.config.from_object(__name__)
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/recognize', methods=['POST'])
def recognize():
    response = recognize_wav(request.data)

    return jsonify(response)


@socketio.on('begin')
def begin_recognition(message):
    session['recognizer'] = OnlineASR(emit)


@socketio.on('chunk')
def recognize_chunk(message):
    session['recognizer'].recognize_chunk(message)


@socketio.on('end')
def end_recognition(message):
    session['recognizer'].end()


if __name__ == '__main__':
    app.secret_key = 12345
    socketio.run(app)
