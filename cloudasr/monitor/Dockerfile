FROM ufaldsg/cloud-asr-base

MAINTAINER Ondrej Klejch

RUN pip install flask flask-socketio==2.0 Werkzeug==0.14.1

ADD . /opt/app
WORKDIR /opt/app
CMD python run.py
