#!/bin/bash

set -e

sudo apt-get install -y libtool autoconf automake uuid-dev build-essential
cd ~
wget http://download.zeromq.org/zeromq-3.2.2.tar.gz
tar zxvf zeromq-3.2.2.tar.gz && cd zeromq-3.2.2
./configure
make && sudo make install

sudo pip install pyzmq
