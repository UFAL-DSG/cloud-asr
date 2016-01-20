#!/bin/bash

mkdir /model
wget -O /model/mfcc.conf https://vystadial.ms.mff.cuni.cz/download/cloudasr/en_wiki/mfcc.conf
wget -O /model/tri2b_bmmi.mdl https://vystadial.ms.mff.cuni.cz/download/cloudasr/en_wiki/tri2b_bmmi.mdl
wget -O /model/tri2b_bmmi.mat https://vystadial.ms.mff.cuni.cz/download/cloudasr/en_wiki/tri2b_bmmi.mat
wget -O /model/HCLG_tri2b_bmmi.fst https://vystadial.ms.mff.cuni.cz/download/cloudasr/en_wiki/HCLG_tri2b_bmmi.fst
wget -O /model/words.txt https://vystadial.ms.mff.cuni.cz/download/cloudasr/en_wiki/words.txt

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
--lattice-beam=0.2
--max-active=4000
EOF

cat << EOF > /model/decodable.cfg
--acoustic-scale=0.1
EOF

cat << EOF > /model/endpoint.cfg
--endpoint.silence_phones=1:2:3:4:5:6:7:8:9:10:11:12:13:14:15:16:17:18:19:20:21:22:23:24:25:26:27:28:29:30:31:32:33:34:35
EOF

cat << EOF > /model/splice.conf
--left-context=4
--right-context=4
EOF
