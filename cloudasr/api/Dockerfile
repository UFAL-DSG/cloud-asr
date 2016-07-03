FROM ufaldsg/cloud-asr-base

MAINTAINER Ondrej Klejch

RUN apt-get install -y libmysqlclient-dev
RUN pip install flask flask-cors flask-sockets flask-sqlalchemy MySQL-python

ADD . /opt/app
WORKDIR /opt/app
CMD while true; do python run.py; done
