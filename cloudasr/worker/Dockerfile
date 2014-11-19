FROM ufaldsg/cloud-asr-base
MAINTAINER Ondrej Klejch

#
# Install PyKaldi.
#
# Prerequesities.
RUN apt-get update
RUN apt-get install -y build-essential libatlas-base-dev python-dev python-pip git wget
# Add pykaldi source files
WORKDIR /app
RUN git clone -b fix-kaldi-changes https://github.com/UFAL-DSG/pykaldi.git
WORKDIR /app/pykaldi
# PyKaldi tools.
WORKDIR tools
RUN make atlas openfst
# Compile the Kaldi src.
WORKDIR ../src
RUN ./configure --shared && make && echo 'KALDI LIBRARY INSTALLED OK'
# Compile Online recogniser.
WORKDIR onl-rec
RUN make && make test && echo 'OnlineLatgenRecogniser build and test OK'
# Compile Kaldi module for Python.
WORKDIR ../../pykaldi
RUN pip install -r pykaldi-requirements.txt
RUN make install && echo 'Pykaldi build and installation files prepared: OK'
# Install locally installed Openfst to /usr/local
WORKDIR ../tools/openfst
RUN for dir in lib include bin ; do cp -r $dir /usr/local/ ; done
RUN ldconfig
# Test setup
RUN python -c 'import fst; import kaldi.decoders'
# Remove Pykaldi source files
WORKDIR /app
RUN rm -rf pykaldi

WORKDIR /opt/app
ADD download_models.sh /opt/app/download_models.sh
RUN bash download_models.sh

ADD . /opt/app
CMD while true; do python run.py; done
