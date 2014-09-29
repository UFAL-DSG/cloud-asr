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

#
# Install PyKaldi.
#

# Prerequesities.
RUN apt-get update
RUN apt-get install -y libatlas-base-dev python-dev python-pip git

WORKDIR /opt
RUN git clone https://github.com/UFAL-DSG/pykaldi/

# PyKaldi tools.
WORKDIR /opt/pykaldi/tools
RUN make atlas openfst_tgt

# Compile the Kaldi src.
WORKDIR /opt/pykaldi/src
RUN ./configure --shared && make depend && make && echo 'KALDI LIBRARY INSTALLED OK'

# Compile Online recogniser.
WORKDIR /opt/pykaldi/src/onl-rec
RUN make && make test && echo 'OnlineLatgenRecogniser build OK'

# Compile Kaldi module for Python.
WORKDIR /opt/pykaldi/pykaldi
RUN pip install -r pykaldi-requirements.txt
RUN make deploy && echo 'Pykaldi build and installation files prepared: OK'

ENV LD_LIBRARY_PATH /opt/pykaldi/pykaldi/pykaldi_Ubuntu_14.04.1_LTS/openfst/lib/
ENV PYTHONPATH $PYTHONPATH:/opt/pykaldi/pykaldi/pyfst/:/opt/pykaldi/pykaldi/

ADD . /opt/app
WORKDIR /opt/app
CMD python run.py
