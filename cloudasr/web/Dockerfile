FROM ufaldsg/cloud-asr-base

MAINTAINER Ondrej Klejch

RUN apt-get install -y libmysqlclient-dev
RUN pip install flask flask-login==0.2.11 flask-googlelogin flask-principal flask-sqlalchemy sqlalchemy MySQL-python Werkzeug==0.9.6 gunicorn==19.1.1

ADD . /opt/app
WORKDIR /opt/app
CMD while true; do python run.py; done
