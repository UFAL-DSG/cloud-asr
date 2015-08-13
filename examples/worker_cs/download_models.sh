#!/bin/bash

mkdir /opt/models
wget -O /opt/models/mfcc.conf https://vystadial.ms.mff.cuni.cz/download/cloudasr/cs/mfcc.conf
wget -O /opt/models/tri2b_bmmi.mdl https://vystadial.ms.mff.cuni.cz/download/cloudasr/cs/tri2b_bmmi.mdl
wget -O /opt/models/tri2b_bmmi.mat https://vystadial.ms.mff.cuni.cz/download/cloudasr/cs/tri2b_bmmi.mat
wget -O /opt/models/HCLG_tri2b_bmmi.fst https://vystadial.ms.mff.cuni.cz/download/cloudasr/cs/HCLG_tri2b_bmmi.fst
wget -O /opt/models/words.txt https://vystadial.ms.mff.cuni.cz/download/cloudasr/cs/words.txt
