import os
import gevent
from flask import Flask, flash, request, jsonify, render_template, redirect, url_for
from flask.ext.socketio import SocketIO
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
from flask.ext.googlelogin import GoogleLogin
from lib import create_recordings_saver, create_db_connection, RecordingsModel, UsersModel


app = Flask(__name__)
app.config.update(
    SECRET_KEY = '12345',
    DEBUG = True,
    GOOGLE_LOGIN_CLIENT_ID = os.environ['GOOGLE_LOGIN_CLIENT_ID'],
    GOOGLE_LOGIN_CLIENT_SECRET = os.environ['GOOGLE_LOGIN_CLIENT_SECRET'],
    GOOGLE_LOGIN_SCOPES = 'https://www.googleapis.com/auth/userinfo.email',
)

socketio = SocketIO(app)
login_manager = LoginManager(app)
google_login = GoogleLogin(app, login_manager)

db = create_db_connection(os.environ['CONNECTION_STRING'])
users_model = UsersModel(db)
recordings_model = RecordingsModel(db, os.environ['STORAGE_PATH'], os.environ['DOMAIN'])
saver = create_recordings_saver("tcp://0.0.0.0:5682", recordings_model)


@app.route('/')
def index():
    return render_template('index.html', models=recordings_model.get_models())

@app.route('/recordings/<model_name>')
def recordings(model_name):
    return render_template('recordings.html', recordings=recordings_model.get_recordings(model_name), model_name=model_name)

@app.route('/transcribe')
@app.route('/transcribe/<id>')
def transcribe(id = None):
    if id is None:
        recording = recordings_model.get_random_recording()
    else:
        recording = recordings_model.get_recording(id)

    return render_template('transcribe.html', recording=recording)

@app.route('/transcriptions/<id>')
def transcriptions(id):
    return render_template('transcriptions.html', recording=recordings_model.get_recording(id))

@app.route('/save-transcription', methods=['POST'])
def save_transcription():
    flash('Recording was successfully transcribed')

    recordings_model.add_transcription(
        current_user,
        request.form['id'],
        request.form['transcription'],
        'native_speaker' in request.form,
        'offensive_language' in request.form,
        'not_a_speech' in request.form
    )

    return redirect(url_for('recordings', model_name=request.form['model']))

@app.route('/crowdflower/<model_name>')
def crowdflower(model_name):
    return render_template('crowdflower.html', model_name=model_name)

@app.route('/crowdflower_export/<model_name>')
def crowdflower_export(model_name):
    return "Not implemented yet!"

@app.route('/login/google')
@google_login.oauth2callback
def login_google(token, userinfo, **params):
    login_user(users_model.upsert_user(userinfo))
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.context_processor
def inject_google_login_url():
    return dict(
        google_login_url = google_login.login_url(redirect_uri=url_for('login_google', _external=True)),
        logout_url = url_for('logout')
    )

@login_manager.user_loader
def load_user(id):
    return users_model.get_user(id)


if __name__ == "__main__":
    from gevent import monkey
    monkey.patch_all()

    gevent.spawn(saver.run)
    socketio.run(app, host="0.0.0.0", port=80)
