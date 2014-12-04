import os


basedir = '/opt/models'
wst_path = '%s/words.txt' % basedir
kaldi_config = [
    '--config=%s/mfcc.conf' % basedir,
    '--verbose=0', '--max-mem=10000000000', '--beam=12.0',
    '--acoustic-scale=0.1', '--lattice-beam=0.2', '--max-active=4000',
    '%s/tri2b_bmmi.mdl' % basedir,
    '%s/HCLG_tri2b_bmmi.fst' % basedir,
    '1:2:3:4:5',
    '%s/tri2b_bmmi.mat' % basedir
]
