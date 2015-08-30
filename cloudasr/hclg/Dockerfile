FROM ufaldsg/kams

MAINTAINER Ondrej Klejch, Ondrej Platek
ENV CLOUD_ASR_HCLG=/app/cloud-asr-hclg
RUN echo $KALDI_ROOT $KAMS_ROOT $CLOUD_ASR_HCLG && mkdir -p $CLOUD_ASR_HCLG CLOUD_ASR_HCLG/models /app/data /app/data/output \
    && echo "Use $CLOUD_ASR_HCLG with run -v option for scripts. Using ufaldsg/kams Docker image"
WORKDIR $CLOUD_ASR_HCLG
