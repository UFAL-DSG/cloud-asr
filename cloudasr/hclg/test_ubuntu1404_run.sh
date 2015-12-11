#!/bin/bash
set -e
echo "Assumes all the dependencies from Dockerfile are in path"
# ./download_model.sh
# out_dir_local=$1; shift  # `pwd`/output_hclg_dir
# models_dir_local=$1; shift  # `pwd`/models
models_dir=`pwd`/models
out_dir=test_output
export KALDI_ROOT=/ha/work/people/oplatek/pykaldi/kaldi
export KAMS_ROOT=/ha/work/people/oplatek/kams
export IRSTLM_ROOT=/ha/work/people/oplatek/kams
python run.py \
  --log-level DEBUG \
  --path-sh /ha/work/people/oplatek/kams/kams/path.sh \
  --out-dir $out_dir \
  --lm $models_dir/final.bg.arpa \
  --am $models_dir/tri2b_bmmi.mdl \
  --am-dict $models_dir/lexicon.txt \
  --tree $models_dir/tri2b_bmmi.tree \
  --mat $models_dir/tri2b_bmmi.mat \
  --sil $models_dir/silence.csl \
  --conf $models_dir/mfcc.conf \
  build_dict --lang cs
