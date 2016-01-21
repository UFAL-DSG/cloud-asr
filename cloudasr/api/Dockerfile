FROM ufaldsg/cloud-asr-base

MAINTAINER Ondrej Klejch

RUN apt-get install -y libmysqlclient-dev
RUN pip install flask flask-cors flask-socketio==0.6.0 flask-sqlalchemy MySQL-python Werkzeug==0.9.6 gunicorn==19.1.1

ADD . /opt/app
WORKDIR /opt/app
CMD while true; do gunicorn -c gunicorn_config.py run:app; done
