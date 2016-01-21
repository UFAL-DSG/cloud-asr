#!/bin/bash

rm -rf /model
mkdir -p /model

cd /model
wget -O /model/vad.tffnn https://vystadial.ms.mff.cuni.cz/download/alex/resources/vad/voip/vad_nnt_1196_hu512_hl1_hla3_pf30_nf15_acf_4.0_mfr32000000_mfl1000000_mfps0_ts0_usec00_usedelta0_useacc0_mbo1_bs1000.tffnn
wget "${MODEL_URL}" -O model.zip
unzip model.zip
