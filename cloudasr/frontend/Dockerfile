FROM ufaldsg/cloud-asr-base

MAINTAINER Ondrej Klejch

RUN pip install flask flask-socketio gunicorn

ADD . /opt/app
WORKDIR /opt/app
CMD while true; do gunicorn -c gunicorn_config.py run:app; done
