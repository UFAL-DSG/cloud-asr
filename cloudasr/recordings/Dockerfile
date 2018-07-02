FROM ufaldsg/cloud-asr-base

MAINTAINER Ondrej Klejch

RUN apt-get update
RUN apt-get install -y libmysqlclient-dev
RUN pip install flask flask-socketio==2.0 flask-sqlalchemy MySQL-python Werkzeug==0.14.1

ADD . /opt/app
WORKDIR /opt/app
CMD while true; do python run.py; done
