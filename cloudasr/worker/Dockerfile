FROM ufaldsg/cloud-asr-base
MAINTAINER Ondrej Klejch

RUN apt-get update && \
    apt-get install -y build-essential libatlas-base-dev python-dev python-pip git wget gfortran g++ unzip zlib1g-dev automake autoconf libtool subversion && \
    pip install webrtcvad

WORKDIR /opt/app/
RUN git clone https://github.com/choko/alex-asr.git && \
    cd /opt/app/alex-asr && \
    git checkout 7ab2b0f89de468645e1d00f282aefd48ca9a314d && \
    pip install -r requirements.txt && \
    bash prepare_env.sh && \
    make && \
    python setup.py install

WORKDIR /opt/app/
ADD . /opt/app

ARG MODEL_URL
RUN bash download_models.sh
CMD while true; do python run.py; done
