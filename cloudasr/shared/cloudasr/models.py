import json
import wave
from cloudasr.schema import create_db_session, WorkerType, User, Recording, Hypothesis, Transcription

def create_db_connection(connection_string):
    return create_db_session(connection_string)


class WorkerTypesModel:

    def __init__(self, db):
        self.db = db

    def get_models(self):
        return self.db.query(WorkerType).all()

    def get_available_workers(self):
        workers = []

        for worker in self.db.query(WorkerType).all():
            workers.append({
                'id': worker.id,
                'name': worker.name,
                'description': worker.description
            })

        return workers

    def get_worker_type(self, id):
        return self.db.query(WorkerType).get(id)

    def upsert_worker_type(self, id):
        worker_type = self.get_worker_type(id)

        if not worker_type:
            worker_type = WorkerType(id = id)
            self.db.add(worker_type)
            self.db.commit()

        return worker_type

    def edit_worker(self, id, name, description):
        worker = self.upsert_worker_type(id)
        worker.name = name
        worker.description = description

        self.db.commit()

class RecordingsModel:

    def __init__(self, db, worker_types_model, path = None, url = None):
        self.db = db
        self.worker_types_model = worker_types_model
        self.url = url

        if path is not None:
            self.file_saver = FileSaver(path)

    def get_recordings(self, model):
        return self.db.query(Recording).filter(Recording.model == model).all()

    def get_recording(self, id):
        return self.db.query(Recording).get(int(id))

    def get_random_recording(self, model):
        from sqlalchemy import func
        return self.db.query(Recording) \
            .filter(Recording.model == model) \
            .order_by(Recording.rand_score) \
            .limit(1) \
            .one()

    def save_recording(self, id, part, chunk_id, model, body, frame_rate, alternatives):
        (path, url) = self.file_saver.save_wav(chunk_id, model, body, frame_rate)
        self.save_recording_to_db(id, part, chunk_id, model, path, url, alternatives)

    def save_recording_to_db(self, id, part, chunk_id, model, path, url, alternatives):
        worker_type = self.worker_types_model.upsert_worker_type(model)

        recording = Recording(
            id = chunk_id,
            uuid = id,
            part = part,
            path = path,
            url = self.url + url,
            score = alternatives[0]["confidence"],
            rand_score = alternatives[0]["confidence"]
        )

        worker_type.recordings.append(recording)

        for alternative in alternatives:
            recording.hypotheses.append(Hypothesis(
                text = alternative["transcript"],
                confidence = alternative["confidence"]
            ))

        self.db.add(recording)
        self.db.commit()

    def add_transcription(self, user, id, transcription, native_speaker, offensive_language, not_a_speech):
        transcription = Transcription(
            user_id = user.get_id(),
            text = transcription,
            native_speaker = native_speaker,
            offensive_language = offensive_language,
            not_a_speech = not_a_speech
        )

        recording = self.get_recording(id)
        recording.transcriptions.append(transcription)
        recording.update_score()
        self.db.commit()


class FileSaver:

    def __init__(self, path):
        self.path = path

    def save_wav(self, chunk_id, model, body, frame_rate):
        path = '%s/%s-%d.wav' % (self.path, model, chunk_id)
        url = '/static/data/%s-%d.wav' % (model, chunk_id)

        wav = wave.open(path, 'w')
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(frame_rate)
        wav.writeframes(body)
        wav.close()

        return (path, url)


class UsersModel:

    def __init__(self, db):
        self.db = db

    def get_user(self, id):
        return self.db.query(User).get(int(id))

    def upsert_user(self, userinfo):
        user = self.get_user(userinfo['id'])

        if user:
            user.email = userinfo['email']
            user.name = userinfo['name']
            user.avatar = userinfo['picture']
        else:
            user = User(
                id = int(userinfo['id']),
                email = userinfo['email'],
                name = userinfo['name'],
                avatar = userinfo['picture']
            )

        self.db.add(user)
        self.db.commit()

        return user


