FROM ufaldsg/cloud-asr-base

MAINTAINER Ondrej Klejch

RUN apt-get install sqlite3
RUN pip install flask flask-socketio sqlalchemy

ADD . /opt/app
WORKDIR /opt/app
CMD while true; do python run.py; done
