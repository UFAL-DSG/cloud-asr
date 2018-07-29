FROM ufaldsg/cloud-asr-base

MAINTAINER Ondrej Klejch

RUN pip install flask==0.10.1 flask-socketio==0.6.0 Werkzeug==0.9.6

ADD . /opt/app
WORKDIR /opt/app
CMD python run.py
