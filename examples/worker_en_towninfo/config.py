import os


basedir = '/opt/models'
wst_path = '%s/words.txt' % basedir
kaldi_config = [
    '--config=%s/mfcc.conf' % basedir,
    '--verbose=0', '--max-mem=10000000000', '--beam=12.0',
    '--acoustic-scale=0.2', '--lattice-beam=2.0', '--max-active=5000',
    '%s/tri2b_bmmi.mdl' % basedir,
    '%s/HCLG_tri2b_bmmi.fst' % basedir,
    '1:2:3:4:5:6:7:8:9:10:11:12:13:14:15:16:17:18:19:20:21:22:23:24:25',
    '%s/tri2b_bmmi.mat' % basedir
]
