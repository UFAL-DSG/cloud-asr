import random
import struct
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, Boolean, ForeignKey, create_engine, types
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql.base import MSBinary

db = SQLAlchemy()

class UUID(types.TypeDecorator):
    impl = MSBinary

    def __init__(self):
        self.impl.length = 16
        types.TypeDecorator.__init__(self, length=self.impl.length)

    def process_bind_param(self, value, dialect=None):
        if value is not None:
            value = int(value)
            return struct.pack('>QQ', (value >> 64), value & ((1 << 64) - 1))
        else:
            return None

    def process_result_value(self, value, dialect=None):
        if value:
            (upper, lower) = struct.unpack('>QQ', value)
            return (upper << 64) | lower
        else:
            return None

    def is_mutable(self):
        return False


class User(db.Model):
    __tablename__ = 'user'

    id = Column(UUID, primary_key = True)
    email = Column(String(128))
    name = Column(String(128))
    avatar = Column(String(128))
    transcriptions = relationship('Transcription', backref="user")
    admin = Column(Boolean)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


class WorkerType(db.Model):
    __tablename__ = 'worker_type'

    id = Column(String(32), primary_key = True)
    lang = Column(String(10))
    name = Column(String(128))
    description = Column(Text)
    visible = Column(Boolean, default = False)
    language_models = relationship('LanguageModel')
    recordings = relationship('Recording')

class LanguageModel(db.Model):
    __tablename__ = 'language_model'

    id = Column(Integer, primary_key = True)
    key = Column(String(32))
    name = Column(String(32))
    worker_type = Column(String(32), ForeignKey('worker_type.id'))

class Recording(db.Model):
    __tablename__ = 'recording'

    id = Column(UUID, primary_key = True)
    uuid = Column(UUID)
    part = Column(Integer)
    model = Column(String(32), ForeignKey('worker_type.id'))
    path = Column(String(128))
    url = Column(String(128))
    best_transcription = Column(Text)
    score = Column(Float)
    created = Column(DateTime, default = datetime.datetime.utcnow)
    hypotheses = relationship('Hypothesis')
    transcriptions = relationship('Transcription')


class Hypothesis(db.Model):
    __tablename__ = 'hypothesis'

    id = Column(Integer, primary_key = True)
    recording_id = Column(UUID, ForeignKey('recording.id'))
    text = Column(Text)
    confidence = Column(Float)


class Transcription(db.Model):
    __tablename__ = 'transcription'

    id = Column(Integer, primary_key = True)
    recording_id = Column(UUID, ForeignKey('recording.id'))
    user_id = Column(UUID, ForeignKey('user.id'), nullable = True)
    text = Column(Text)
    created = Column(DateTime, default = datetime.datetime.utcnow)
    has_been_played = Column(Boolean)
    native_speaker = Column(Boolean)
    offensive_language = Column(Boolean)
    not_a_speech = Column(Boolean)

