FROM ufaldsg/cloud-asr-base

MAINTAINER Ondrej Klejch

RUN pip install flask flask-socketio

ADD . /opt/app
WORKDIR /opt/app
CMD while true; do python run.py; done
