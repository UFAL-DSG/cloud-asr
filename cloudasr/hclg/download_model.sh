#!/bin/bash

am_dir="`dirname \"$0\"`"/models
mkdir -p $am_dir
pushd $am_dir
echo "Using a medium AM"
wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/en_super_no_dnn-2015-04-16--17-44-34-s4k-g100k/tri2b_bmmi.mdl
wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/en_super_no_dnn-2015-04-16--17-44-34-s4k-g100k/tri2b_bmmi.tree
wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/en_super_no_dnn-2015-04-16--17-44-34-s4k-g100k/tri2b_bmmi.mat
wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/en_super_no_dnn-2015-04-16--17-44-34-s4k-g100k/mfcc.conf
wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/en_super_no_dnn-2015-04-16--17-44-34-s4k-g100k/silence.csl
wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/en_super_no_dnn-2015-04-16--17-44-34-s4k-g100k/phones.txt

#echo "Using a large AM - does not work that well"
#wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/en_super_no_dnn-2015-04-23--05-40-30-s8k-g200k/tri2b_bmmi.mdl
#wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/en_super_no_dnn-2015-04-23--05-40-30-s8k-g200k/tri2b_bmmi.tree
#wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/en_super_no_dnn-2015-04-23--05-40-30-s8k-g200k/tri2b_bmmi.mat
#wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/en_super_no_dnn-2015-04-23--05-40-30-s8k-g200k/mfcc.conf
#wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/en_super_no_dnn-2015-04-23--05-40-30-s8k-g200k/silence.csl
#wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/en_super_no_dnn-2015-04-23--05-40-30-s8k-g200k/phones.txt
popd
