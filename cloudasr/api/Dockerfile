FROM ufaldsg/cloud-asr-base

MAINTAINER Ondrej Klejch

RUN apt-get update
RUN apt-get install -y libmysqlclient-dev
RUN pip install flask flask-cors flask-socketio==2.0 gunicorn[gevent] python-socketio gevent-websocket  MySQL-python Werkzeug==0.14.1 flask-sqlalchemy

ADD . /opt/app
WORKDIR /opt/app
CMD while true; do gunicorn -c gunicorn_config.py run:app; done
