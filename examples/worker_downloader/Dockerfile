FROM ufaldsg/cloud-asr-worker
MAINTAINER Ondrej Klejch

WORKDIR /opt/app
ADD download_models.sh /opt/app/download_models.sh

CMD bash download_models.sh && ( while true; do python run.py; done )
