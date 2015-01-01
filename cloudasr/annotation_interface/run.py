import gevent
from flask import Flask, flash, request, jsonify, render_template, redirect, url_for
from flask.ext.socketio import SocketIO
from lib import create_recordings_saver, RecordingsModel


app = Flask(__name__)
app.secret_key = '12345'
app.config['DEBUG'] = True
socketio = SocketIO(app)
saver = create_recordings_saver("tcp://0.0.0.0:5682", "/opt/app/static/data")
model = RecordingsModel("/opt/app/static/data")

@app.route('/')
def index():
    return render_template('index.html', recordings=model.get_recordings())

@app.route('/transcribe/<id>')
def transcribe(id):
    return render_template('transcribe.html', recording=model.get_recording(id))

@app.route('/save-transcription', methods=['POST'])
def save_transcription():
    flash('Recording was successfully transcribed')
    model.add_transcription(request.form['id'], request.form['transcription'])
    return redirect(url_for('index'))


if __name__ == "__main__":
    from gevent import monkey
    monkey.patch_all()

    gevent.spawn(saver.run)
    socketio.run(app, host="0.0.0.0", port=80)
