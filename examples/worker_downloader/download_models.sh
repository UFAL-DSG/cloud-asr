#!/bin/bash

mkdir -p /opt/models
wget -O /opt/models/mfcc.conf $MFCC_CONF_URL
wget -O /opt/models/tri2b_bmmi.mdl $TRI2B_BMMI_MDL_URL
wget -O /opt/models/tri2b_bmmi.mat $TRI2B_BMMI_MAT_URL
wget -O /opt/models/HCLG_tri2b_bmmi.fst $HCLG_TRI2B_BMMI_FST_URL
wget -O /opt/models/words.txt $WORDS_TXT_URL
wget -O /opt/app/config.py $CONFIG_PY_URL
