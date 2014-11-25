FROM ufaldsg/cloud-asr-worker
MAINTAINER Ondrej Klejch

WORKDIR /opt/app
ADD . /opt/app
RUN bash download_models.sh

ENV model cs-alex
