#!/bin/bash

am_dir="`dirname \"$0\"`"/models
mkdir -p $am_dir
pushd $am_dir 2> /dev/null
echo "TODO english models needs to be udpated and contain lexicon.txt Using a medium AM"
# wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/en_super_no_dnn-2015-04-16--17-44-34-s4k-g100k/tri2b_bmmi.mdl
# wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/en_super_no_dnn-2015-04-16--17-44-34-s4k-g100k/tri2b_bmmi.tree
# wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/en_super_no_dnn-2015-04-16--17-44-34-s4k-g100k/tri2b_bmmi.mat
# wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/en_super_no_dnn-2015-04-16--17-44-34-s4k-g100k/mfcc.conf
# wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/en_super_no_dnn-2015-04-16--17-44-34-s4k-g100k/silence.csl
# wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/en_super_no_dnn-2015-04-16--17-44-34-s4k-g100k/phones.txt
#

wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/cs_super_s2k_g50k-2015-09-29--01-51-08/tri2b_bmmi.mdl
wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/cs_super_s2k_g50k-2015-09-29--01-51-08/tri2b_bmmi.tree
wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/cs_super_s2k_g50k-2015-09-29--01-51-08/tri2b_bmmi.mat
wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/cs_super_s2k_g50k-2015-09-29--01-51-08/mfcc.conf
wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/cs_super_s2k_g50k-2015-09-29--01-51-08/silence.csl
wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/cs_super_s2k_g50k-2015-09-29--01-51-08/phones.txt
wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/kams/cs_super_s2k_g50k-2015-09-29--01-51-08/lexicon.txt


wget --timestamping  https://vystadial.ms.mff.cuni.cz/download/alex/applications/PublicTransportInfoCS/lm/final.bg.arpa

popd 2> /dev/null
