import os
from flask import Flask, Response, flash, render_template, redirect, request, url_for, session, jsonify, stream_with_context
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_googlelogin import GoogleLogin
from flask_principal import Principal, Permission, RoleNeed, UserNeed, AnonymousIdentity, Identity, identity_loaded, identity_changed
from flask_sqlalchemy import SQLAlchemy
from lib import run_worker_on_marathon
from cloudasr.schema import db
from cloudasr.models import UsersModel, RecordingsModel, WorkerTypesModel


app = Flask(__name__)
app.config.update(
    SECRET_KEY = '12345',
    DEBUG = 'DEBUG' in os.environ,
    GOOGLE_LOGIN_CLIENT_ID = os.environ['GOOGLE_LOGIN_CLIENT_ID'],
    GOOGLE_LOGIN_CLIENT_SECRET = os.environ['GOOGLE_LOGIN_CLIENT_SECRET'],
    GOOGLE_LOGIN_SCOPES = 'https://www.googleapis.com/auth/userinfo.email',
    SQLALCHEMY_DATABASE_URI = os.environ['CONNECTION_STRING']
)

login_manager = LoginManager(app)
google_login = GoogleLogin(app, login_manager)

principals = Principal(app)
admin_permission = Permission(RoleNeed('admin'))

db.init_app(app)
users_model = UsersModel(db.session)
worker_types_model = WorkerTypesModel(db.session)
recordings_model = RecordingsModel(db.session, worker_types_model)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/demo')
@app.route('/demo/<model>')
def demo(model=None):
    return render_template('demo.html', api_url = os.environ['API_URL'], model = model)

@app.route('/available-workers')
def available_workers():
    return jsonify({"workers": worker_types_model.get_available_workers()})

@app.route('/documentation')
def documentation():
    return render_template('documentation.html')

@app.route('/worker-types')
def worker_types():
    return render_template('worker_types.html', worker_types=worker_types_model.get_models())

@app.route('/transcribe/<model>')
@app.route('/transcribe/<int:id>')
def transcribe(id = None, model = None):
    if id is not None:
        recording = recordings_model.get_recording(id)
        backlink = request.args.get('next') or url_for('transcribe', model = recording.model)

    if model is not None:
        recording = recordings_model.get_random_recording(model)
        backlink = url_for('transcribe', model = model)

    return render_template('transcribe.html', recording=recording, backlink=backlink)

@app.route('/save-transcription', methods=['POST'])
def save_transcription():
    flash('Recording was successfully transcribed')

    recordings_model.add_transcription(
        current_user.get_id(),
        request.form['id'],
        request.form['transcription'],
        'native_speaker' in request.form,
        'offensive_language' in request.form,
        'not_a_speech' in request.form
    )

    return redirect(request.form['backlink'])

@app.route('/recordings/<model>/<int:page>')
@admin_permission.require()
def recordings(model, page):
    pagination = recordings_model.get_recordings(model).paginate(page, 10)
    recordings = pagination.items


    return render_template('recordings.html', recordings=recordings, model=model, pagination=pagination)

@app.route('/transcriptions/<id>')
@admin_permission.require()
def transcriptions(id):
    return render_template('transcriptions.html', recording=recordings_model.get_recording(id))

@app.route('/accept-transcription/<int:recording>/<transcription>', methods=['GET'])
@admin_permission.require()
def accept_transcription(recording, transcription):
    recordings_model.set_transcription(recording, transcription)
    return redirect(url_for('transcriptions', id = recording))

@app.route('/crowdflower/<model>')
def crowdflower(model):
    return render_template('crowdflower.html', model = model)

@app.route('/crowdflower-export/<model>.csv')
def crowdflower_export(model):
    def generate():
        yield "url\n"
        for row in recordings_model.get_random_recordings(model):
            yield "%s\n" % row.url

    return Response(stream_with_context(generate()), mimetype='text/csv')

@app.route('/upload-results')
def upload_results():
    return render_template('upload_results.html')

@app.route('/upload-results-file', methods=['POST'])
def upload_results_file():
    if recordings_model.load_transcriptions(request.files['file']):
        flash('Results were uploaded successfully.', 'success')
    else:
        flash('There was an error during the results upload.', 'danger')

    return redirect(url_for('upload_results'))


@app.route('/kaldi-worker')
def kaldi_worker():
    return render_template('kaldi_worker.html', worker = {"id": None})

@app.route('/new-worker')
@admin_permission.require()
def new_worker():
    return render_template('edit_worker.html', worker = {"id": None})

@app.route('/edit-worker/<model>')
@admin_permission.require()
def edit_worker(model):
    return render_template('edit_worker.html', worker = worker_types_model.get_worker_type(model))

@app.route('/toggle-worker-visibility/<model>/<visibility>')
def toggle_worker_visibility(model, visibility):
    visible = visibility == "True"
    worker_types_model.toggle_worker_visibility(model, visible)

    if visible:
        flash("Worker %s is now visible." % model)
    else:
        flash("Worker %s is now hidden." % model)

    return redirect(url_for('worker_types'))

@app.route('/save-worker-description', methods=['POST'])
@admin_permission.require()
def save_worker_description():
    if request.form.get('run_on_marathon', False):
        url = os.environ.get("MARATHON_URL", None)
        login = os.environ.get("MARATHON_LOGIN", None)
        password = os.environ.get("MARATHON_PASSWORD", None)
        config = {
            "id": request.form["id"],
            "model_url": request.form["model_url"],
            "cpu": request.form["cpu"],
            "mem": request.form["mem"],
            "master_addr": os.environ.get("MASTER_ADDR", None),
            "recordings_saver_addr": os.environ.get("RECORDINGS_SAVER_ADDR", None)
        }

        if not run_worker_on_marathon(url, login, password, config):
            flash('Worker wasn\'t started successfully')
            return redirect(url_for('kaldi_worker'))

    flash('Worker\'s description was successfully saved')
    worker_types_model.edit_worker(
        request.form['id'],
        request.form['name'],
        request.form['description'],
        request.form.getlist("lm-id[]"),
        request.form.getlist("lm-name[]")
    )

    return redirect(url_for('worker_types'))

@app.route('/delete-worker/<model>')
@admin_permission.require()
def delete_worker(model):
    worker_types_model.delete_worker(model)
    flash("Worker was successfully deleted")
    return redirect(url_for('worker_types'))

@app.route('/login/google')
@google_login.oauth2callback
def login_google(token, userinfo, **params):
    login_user(users_model.upsert_user(userinfo))

    identity = Identity(userinfo['id'])
    identity_changed.send(app, identity = identity)

    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()

    for key in ['identity.name', 'identity.auth_type']:
        session.pop(key, None)
    identity_changed.send(app, identity=AnonymousIdentity())

    return redirect(url_for('index'))

@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

@app.context_processor
def inject_google_login_url():
    return dict(
        google_login_url = google_login.login_url(redirect_uri=url_for('login_google', _external=True)),
        ga_tracking_id = os.environ.get('GA_TRACKING_ID', None),
        logout_url = url_for('logout')
    )

@login_manager.user_loader
def load_user(id):
    return users_model.get_user(id)

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity.user = current_user

    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    if hasattr(current_user, 'admin') and current_user.admin:
        identity.provides.add(RoleNeed('admin'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
