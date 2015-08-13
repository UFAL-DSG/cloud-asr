#!/bin/bash

mkdir /opt/models
wget -O /opt/models/mfcc.conf https://vystadial.ms.mff.cuni.cz/download/pykaldi/egs/vystadial/online_demo/models_en/mfcc.conf
wget -O /opt/models/tri2b_bmmi.mdl https://vystadial.ms.mff.cuni.cz/download/pykaldi/egs/vystadial/online_demo/models_en/tri2b_bmmi.mdl
wget -O /opt/models/tri2b_bmmi.mat https://vystadial.ms.mff.cuni.cz/download/pykaldi/egs/vystadial/online_demo/models_en/tri2b_bmmi.mat
wget -O /opt/models/HCLG_tri2b_bmmi.fst https://vystadial.ms.mff.cuni.cz/download/pykaldi/egs/vystadial/online_demo/models_en/HCLG_tri2b_bmmi.fst
wget -O /opt/models/words.txt https://vystadial.ms.mff.cuni.cz/download/pykaldi/egs/vystadial/online_demo/models_en/words.txt
wget -O /opt/models/vad.tffnn https://vystadial.ms.mff.cuni.cz/download/alex/resources/vad/voip/vad_nnt_1196_hu512_hl1_hla3_pf30_nf15_acf_4.0_mfr32000000_mfl1000000_mfps0_ts0_usec00_usedelta0_useacc0_mbo1_bs1000.tffnn
