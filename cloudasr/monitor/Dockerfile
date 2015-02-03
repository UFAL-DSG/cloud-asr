FROM ufaldsg/cloud-asr-base

MAINTAINER Ondrej Klejch

RUN pip install flask flask-socketio Werkzeug==0.9.6

ADD . /opt/app
WORKDIR /opt/app
CMD python run.py
