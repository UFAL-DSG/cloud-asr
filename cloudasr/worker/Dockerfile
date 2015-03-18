FROM ufaldsg/cloud-asr-base
MAINTAINER Ondrej Klejch

RUN apt-get update && \
    apt-get install -y build-essential libatlas-base-dev python-dev python-pip git wget gfortran && \
    pip install theano

WORKDIR /app
RUN git clone https://github.com/UFAL-DSG/pykaldi.git && \
    cd pykaldi && \
    git checkout 1a71ef6a1f1b6a228c72c3637410bb86daea0d5c && \
    cd /app/pykaldi/tools && \
    make atlas openfst && \
    cd /app/pykaldi/src && \
    ./configure --shared && make && echo 'KALDI LIBRARY INSTALLED OK' && \
    cd /app/pykaldi/src/onl-rec && \
    make && make test && echo 'OnlineLatgenRecogniser build and test OK' && \
    cd /app/pykaldi/pykaldi && \
    pip install -r pykaldi-requirements.txt && \
    make install && echo 'Pykaldi build and installation files prepared: OK' && \
    cd /app/pykaldi/tools/openfst && \
    for dir in lib include bin ; do cp -r $dir /usr/local/ ; done && \
    ldconfig && \
    python -c 'import fst; import kaldi.decoders' && \
    cd /app && \
    rm -rf pykaldi

WORKDIR /opt/app
ADD download_models.sh /opt/app/download_models.sh
RUN bash download_models.sh

ADD . /opt/app
CMD while true; do python run.py; done
