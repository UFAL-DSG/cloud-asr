FROM ufaldsg/cloud-asr-base

MAINTAINER Ondrej Klejch

RUN apt-get update && apt-get install -y libmysqlclient-dev
RUN pip install flask==0.10.1 flask-cors==2.1.2 flask-socketio==0.6.0 flask-sqlalchemy==2.1 MySQL-python==1.2.5 Werkzeug==0.9.6 gunicorn==19.1.1

ADD . /opt/app
WORKDIR /opt/app
CMD while true; do gunicorn -c gunicorn_config.py run:app; done
