FROM ubuntu:14.04

MAINTAINER Ondrej Klejch

RUN apt-get update
RUN apt-get install -y wget build-essential

RUN wget http://download.zeromq.org/zeromq-3.2.4.tar.gz
RUN tar xzf zeromq-3.2.4.tar.gz
WORKDIR /zeromq-3.2.4
RUN ./configure && make && make install
RUN ldconfig

RUN apt-get install -y python python-dev python-distribute python-pip
RUN pip install pyzmq

RUN pip install nose

ADD . /opt/app
WORKDIR /opt/app
CMD python run.py
