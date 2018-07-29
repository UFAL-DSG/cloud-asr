FROM ufaldsg/cloud-asr-base

MAINTAINER Ondrej Klejch

RUN apt-get update && apt-get install -y libmysqlclient-dev
RUN pip install flask==0.10.1 flask-login==0.2.11 flask-googlelogin==0.3.1 flask-principal==0.4.0 flask-sqlalchemy==2.1 sqlalchemy==1.0.11 MySQL-python==1.2.5 Werkzeug==0.9.6 gunicorn==19.1.1

ADD . /opt/app
WORKDIR /opt/app
CMD while true; do python run.py; done
