FROM ufaldsg/kams

MAINTAINER Ondrej Klejch, Ondrej Platek
ADD . /app/cloud-asr-hclg
WORKDIR /app/cloud-asr-hclg
CMD while true; do python run.py; echo "Command finished"; date; echo; sleep 1; done
