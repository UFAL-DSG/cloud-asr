FROM ufaldsg/cloud-asr-base

MAINTAINER Ondrej Klejch

RUN apt-get install -y libmysqlclient-dev
RUN pip install flask flask-socketio flask-sqlalchemy MySQL-python Werkzeug==0.9.6

ADD . /opt/app
WORKDIR /opt/app
CMD while true; do python run.py; done
