FROM ufaldsg/cloud-asr-base

MAINTAINER Ondrej Klejch

RUN apt-get install sqlite3
RUN pip install flask flask-socketio

ADD . /opt/app
WORKDIR /opt/app
RUN sqlite3 db < schema.sql
CMD while true; do python run.py; done
