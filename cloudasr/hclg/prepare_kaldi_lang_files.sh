#!/bin/bash
# Copyright (c) 2013, Ondrej Platek, Ufal MFF UK <oplatek@ufal.mff.cuni.cz>
# encoding: utf-8
# Licensed under the Apache License, Version 2.0 (the "License");
#
# This script creates a fully expanded decoding graph (HCLG),
# which is domain dependent.
#
# It supposes the same phone lists generated from lexicon are the same
# as used for training AM! It is up to you to check it!
#
# The HCLG graph represents language model,
# pronunciation dictionary (lexicon),
# phonetic context-dependency and HMM structure.
#
# The output is a Finite State Transduser (FST),
# that has word-ids on the output, pdf-ids on the input.
# The pdf-ids are indexes that resolve to Gaussian Mixture Models.
# See http://kaldi.sourceforge.net/graph_recipe_test.html.
# based on egs/voxforge script created by  Vassil Panayotov Copyright 2012, Apache 2.0
# FIXME rewrite to Python


# FIXME move to separate script
#######################################################################
#                 End of param parsing - setting ENV                  #
#######################################################################

# creating symlinks to scripts which wraps kaldi binaries
if [[ -z "$KALDI_ROOT" ]] ; then
    echo; echo "KALDI_ROOT need to be set"; echo
    exit 1
fi

symlinks="$KALDI_ROOT/egs/wsj/s5/steps $KALDI_ROOT/egs/wsj/s5/utils"
for syml in $symlinks ; do
    name=`basename $syml`
    if [ ! -e "$name" ] ; then
        ln -f -s "$syml"
        if [ -e $name ] ; then
            echo "Created symlink $syml -> $name"
        else
            echo "Failed to create symlink $syml -> $name"
            exit 1
        fi
    fi
    export PATH="$PWD/$name":$PATH
done

#######################################################################
#               End of setting ENV - running the script               #
#######################################################################

if [[  $# -ne 11 ]]; then
  echo; echo "Usage:"; echo
  echo "$0 <AM.mdl> <tree> <mfcc.conf> <matrix.mat> <silence.csl> <dict.txt> <vocab.txt> <LM.arpa> <OOV> <local-tmp-dir> <out-models-dir>"
  echo ""
  echo "Set also '\$KALDI_ROOT' variable before running the script'"
  echo ""
  echo "See http://kaldi.sourceforge.net/data_prep.html#data_prep_lang_creating and "
  echo "http://kaldi.sourceforge.net/graph_recipe_test.html for more info."
  echo ""
  exit 1;
fi

. utils/parse_options.sh

model=$1; shift
tree=$1; shift

conf=$1; shift
mat=$1; shift
sil=$1; shift

dictionary=$1; shift
vocabulary=$1; shift
lm_arpa=$1; shift

oov_word=$1; shift  # prepare_lang.sh <UNK>

locdata=$1; shift
locdict=$locdata/dict
# tmpdir=$locdata/lang
tmpdir=$locdata/tmp
hclg=$locdata/hclg
lang=$locdata/lang

dir=$1; shift  # output dir




echo ; echo "Running utils/prepare_lang.sh" ; echo

echo "utils/prepare_lang.sh $locdict $oov_word $tmpdir $lang"
utils/prepare_lang.sh $locdict $oov_word $tmpdir $lang || exit 1



echo; echo "--- Preparing the grammar transducer (G.fst) ..." ; echo

cat $lm_arpa | \
   utils/find_arpa_oovs.pl $lang/words.txt > $tmpdir/oovs.txt

 # grep -v '<s> <s>' because the LM seems to have some strange and useless
 # stuff in it with multiple <s>'s in the history.  Encountered some other similar
 # things in a LM from Geoff.  Removing all "illegal" combinations of <s> and </s>,
 # which are supposed to occur only at being/end of utt.  These can cause
 # determinization failures of CLG [ends up being epsilon cycles].

cat $lm_arpa | \
  grep -v '<s> <s>\|</s> <s>\|</s> </s>' | \
  arpa2fst - | fstprint | \
  utils/remove_oovs.pl $tmpdir/oovs.txt | \
  utils/eps2disambig.pl | utils/s2eps.pl | fstcompile --isymbols=$lang/words.txt \
    --osymbols=$lang/words.txt  --keep_isymbols=false --keep_osymbols=false | \
  fstrmepsilon > $lang/G.fst

# Everything below is only for diagnostic.
fstisstochastic $lang/G.fst
# The output is like:
# 9.14233e-05 -0.259833
# we do expect the first of these 2 numbers to be close to zero (the second is
# nonzero because the backoff weights make the states sum to >1).
# Because of the <s> fiasco for these particular LMs, the first number is not
# as close to zero as it could be.

# Checking that G has no cycles with empty words on them (e.g. <s>, </s>);
# this might cause determinization failure of CLG.
# #0 is treated as an empty word.
mkdir -p $tmpdir/g
awk '{if(NF==1){ printf("0 0 %s %s\n", $1,$1); }} END{print "0 0 #0 #0"; print "0";}' \
  < "$locdict/lexicon.txt"  >$tmpdir/g/select_empty.fst.txt
fstcompile --isymbols=$lang/words.txt --osymbols=$lang/words.txt \
  $tmpdir/g/select_empty.fst.txt | \
fstarcsort --sort_type=olabel | fstcompose - $lang/G.fst > $tmpdir/g/empty_words.fst
fstinfo $tmpdir/g/empty_words.fst | grep cyclic | grep -w 'y' &&
  echo "Language model has cycles with empty words" && exit 1
rm -r $tmpdir/g

echo "*** Succeeded in creating G.fst for $lang"
