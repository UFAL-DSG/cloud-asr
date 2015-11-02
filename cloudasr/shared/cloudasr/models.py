import re
import csv
import json
import wave
from cloudasr.schema import WorkerType, LanguageModel, User, Recording, Hypothesis, Transcription


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
                'description': worker.description,
                'language_models': [{"key": lm.key, "name": lm.name} for lm in worker.language_models]
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

    def edit_worker(self, id, name, description, lm_ids, lm_names):
        worker = self.upsert_worker_type(id)
        worker.name = name
        worker.description = description

        for lm in worker.language_models:
            self.db.delete(lm)

        language_models = [(lm_id, lm_name) for (lm_id, lm_name) in zip(lm_ids, lm_names) if lm_id != "" and lm_name != ""]
        for (lm_id, lm_name) in language_models:
            lm = LanguageModel(
                key = lm_id,
                name = lm_name
            )

            worker.language_models.append(lm)

        self.db.commit()

    def delete_worker(self, id):
        worker_type = self.get_worker_type(id)
        self.db.delete(worker_type)
        self.db.commit()


class RecordingsModel:

    def __init__(self, db, worker_types_model, path = None, url = None):
        self.db = db
        self.worker_types_model = worker_types_model
        self.url = url

        if path is not None:
            self.file_saver = FileSaver(path)

    def get_recordings(self, model):
        return Recording.query.filter(Recording.model == model).order_by(Recording.created)

    def get_recording(self, id):
        return self.db.query(Recording).get(int(id))

    def get_random_recording(self, model):
        try:
            from sqlalchemy import func
            return self.db.query(Recording) \
                .filter(Recording.model == model) \
                .filter(Recording.score < 0.8) \
                .order_by(func.rand()) \
                .limit(1) \
                .one()
        except Exception:
            return None

    def get_random_recordings(self, model):
        try:
            from sqlalchemy import func
            return self.db.query(Recording) \
                .filter(Recording.model == model) \
                .filter(Recording.score < 0.8) \
                .order_by(func.rand()) \
                .limit(100) \
                .all()
        except Exception:
            return []

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
        )

        worker_type.recordings.append(recording)

        for alternative in alternatives:
            recording.hypotheses.append(Hypothesis(
                text = alternative["transcript"],
                confidence = alternative["confidence"]
            ))

        self.db.add(recording)
        self.db.commit()

    def load_transcriptions(self, csv_file):
        try:
            csv_reader = csv.reader(csv_file, delimiter = ',')

            headers = csv_reader.next()
            transcribed_text_index = headers.index('transcribed_text')
            url_index = headers.index('url')
            id_matcher = re.compile('.*-(\d+)\.wav')

            transcriptions = []
            for row in csv_reader:
                id =  int(id_matcher.match(row[url_index]).group(1))
                transcription = row[transcribed_text_index]

                transcriptions.append(({"recording_id": id, "text": transcription}))

            self.db.execute(Transcription.__table__.insert(), transcriptions)
            self.db.commit()

            return True
        except Exception, e:
            return False

    def add_transcription(self, user_id, id, transcription, native_speaker = None, offensive_language = None, not_a_speech = None):
        transcription = Transcription(
            user_id = user_id,
            text = transcription,
            native_speaker = native_speaker,
            offensive_language = offensive_language,
            not_a_speech = not_a_speech
        )

        recording = self.get_recording(id)
        if recording == None:
            return False

        recording.transcriptions.append(transcription)
        self.db.commit()

        return True

    def set_transcription(self, id, transcription):
        recording = self.get_recording(id)
        recording.score = 1.0
        recording.best_transcription = transcription
        self.db.commit()

        return True


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


