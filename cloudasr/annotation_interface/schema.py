import struct
import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, create_engine, types
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UUID(types.TypeDecorator):
    impl = types.Binary

    def __init__(self):
        self.impl.length = 16
        types.TypeDecorator.__init__(self, length=self.impl.length)

    def process_bind_param(self, value, dialect=None):
        return struct.pack('>QQ', (value >> 64), value & ((1 << 64) - 1))

    def process_result_value(self, value, dialect=None):
        if value:
            (upper, lower) = struct.unpack('>QQ', value)
            return (upper << 64) | lower
        else:
            return None

    def is_mutable(self):
        return False


class Recording(Base):
    __tablename__ = 'recording'

    id = Column(UUID, primary_key = True)
    model = Column(String)
    path = Column(String)
    url = Column(String)
    hypothesis = Column(String)
    confidence = Column(Float)
    created = Column(DateTime, default = datetime.datetime.utcnow)
    transcripts = relationship('Transcript')

    def to_dict(self):
        d = dict((col, getattr(self, col)) for col in self.__table__.columns.keys())
        d["created"] = str(d["created"])

        return d


class Transcript(Base):
    __tablename__ = 'transcript'

    id = Column(Integer, primary_key = True)
    recording_id = Column(UUID, ForeignKey('recording.id'))
    user_id = Column(Integer)
    transcript = Column(String)


def create_db_session(path):
    engine = create_engine('sqlite:///%s' % path)
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)

    return session
