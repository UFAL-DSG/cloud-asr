FROM ubuntu:18.04

MAINTAINER Ondrej Klejch

RUN apt-get update
RUN apt-get install -y wget build-essential python python-dev python-distribute python-pip python3 python3-dev
RUN pip install --install-option="--zmq=bundled" pyzmq
RUN pip install protobuf==2.6.1 nose==1.3.7 gevent==1.0.2

ADD . /usr/lib/python2.7/dist-packages/
