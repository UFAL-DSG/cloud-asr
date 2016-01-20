#!/bin/bash

mkdir /model
wget -O /model/vad.tffnn https://vystadial.ms.mff.cuni.cz/download/alex/resources/vad/voip/vad_nnt_1196_hu512_hl1_hla3_pf30_nf15_acf_4.0_mfr32000000_mfl1000000_mfps0_ts0_usec00_usedelta0_useacc0_mbo1_bs1000.tffnn
wget -O /model/mfcc.conf https://vystadial.ms.mff.cuni.cz/download/pykaldi/egs/vystadial/online_demo/models_en/mfcc.conf
wget -O /model/tri2b_bmmi.mdl https://vystadial.ms.mff.cuni.cz/download/pykaldi/egs/vystadial/online_demo/models_en/tri2b_bmmi.mdl
wget -O /model/tri2b_bmmi.mat https://vystadial.ms.mff.cuni.cz/download/pykaldi/egs/vystadial/online_demo/models_en/tri2b_bmmi.mat
wget -O /model/HCLG_tri2b_bmmi.fst https://vystadial.ms.mff.cuni.cz/download/pykaldi/egs/vystadial/online_demo/models_en/HCLG_tri2b_bmmi.fst
wget -O /model/words.txt https://vystadial.ms.mff.cuni.cz/download/pykaldi/egs/vystadial/online_demo/models_en/words.txt

cat << EOF > /model/alex_asr.conf
--model_type=gmm
--model=tri2b_bmmi.mdl
--hclg=HCLG_tri2b_bmmi.fst
--words=words.txt
--mat_lda=tri2b_bmmi.mat
--cfg_mfcc=mfcc.conf
--cfg_decoder=decoder.cfg
--cfg_decodable=decodable.cfg
--cfg_endpoint=endpoint.cfg
--cfg_splice=splice.conf
EOF

cat << EOF > /model/decoder.cfg
--beam=12.0
--lattice-beam=2.0
--max-active=5000
EOF

cat << EOF > /model/decodable.cfg
--acoustic-scale=0.2
EOF

cat << EOF > /model/endpoint.cfg
--endpoint.silence_phones=1:2:3:4:5:6:7:8:9:10:11:12:13:14:15:16:17:18:19:20:21:22:23:24:25
EOF

cat << EOF > /model/splice.conf
--left-context=4
--right-context=4
EOF
