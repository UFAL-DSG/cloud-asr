import gevent
from flask import Flask, flash, request, jsonify, render_template, redirect, url_for
from flask.ext.socketio import SocketIO
from lib import create_recordings_saver, create_db_connection, RecordingsModel


app = Flask(__name__)
app.secret_key = '12345'
app.config['DEBUG'] = True
socketio = SocketIO(app)
db = create_db_connection("db")
model = RecordingsModel("/opt/app/static/data", db)
saver = create_recordings_saver("tcp://0.0.0.0:5682", "/opt/app/static/data", model)

@app.route('/')
def index():
    return render_template('index.html', models=model.get_models())

@app.route('/recordings/<model_name>')
def recordings(model_name):
    return render_template('recordings.html', recordings=model.get_recordings(model_name), model_name=model_name)

@app.route('/transcribe')
@app.route('/transcribe/<id>')
def transcribe(id = None):
    if id is None:
        recording = model.get_random_recording()
    else:
        recording = model.get_recording(id)

    return render_template('transcribe.html', recording=recording)

@app.route('/transcriptions/<id>')
def transcriptions(id):
    return render_template('transcriptions.html', recording=model.get_recording(id))

@app.route('/save-transcription', methods=['POST'])
def save_transcription():
    flash('Recording was successfully transcribed')
    model.add_transcription(request.form['id'], request.form['transcription'], request.form['has_been_played'] == '1')
    return redirect(url_for('recordings', model_name=request.form['model']))

@app.route('/crowdflower/<model_name>')
def crowdflower(model_name):
    return render_template('crowdflower.html', model_name=model_name)

@app.route('/crowdflower_export/<model_name>')
def crowdflower_export(model_name):
    return "Not implemented yet!"


if __name__ == "__main__":
    from gevent import monkey
    monkey.patch_all()

    gevent.spawn(saver.run)
    socketio.run(app, host="0.0.0.0", port=80)
