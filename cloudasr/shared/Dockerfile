FROM ubuntu:14.04

MAINTAINER Ondrej Klejch

RUN apt-get update
RUN apt-get install -y wget build-essential python python-dev python-distribute python-pip
RUN pip install --install-option="--zmq=bundled" pyzmq
RUN pip install protobuf nose gevent

ADD . /usr/lib/python2.7/dist-packages/
