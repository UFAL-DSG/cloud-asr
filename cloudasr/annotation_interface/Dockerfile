FROM ufaldsg/cloud-asr-base

MAINTAINER Ondrej Klejch

RUN apt-get install sqlite3
RUN pip install flask flask-socketio flask-login flask-googlelogin sqlalchemy Werkzeug==0.9.6

ADD . /opt/app
WORKDIR /opt/app
CMD while true; do python run.py; done
