FROM ufaldsg/kams

MAINTAINER Ondrej Klejch, Ondrej Platek
ENV CLOUD_ASR_HCLG=/app/cloud-asr-hclg
RUN echo $KALDI_ROOT KAMS_ROOT $CLOUD_ASR_HCLG && mkdir -p $CLOUD_ASR_HCLG /app/data
ADD . $CLOUD_ASR_HCLG
WORKDIR $CLOUD_ASR_HCLG
