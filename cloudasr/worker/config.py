import os


basedir = os.path.dirname(os.path.realpath(__file__))
wst_path = '%s/models/words.txt' % basedir
kaldi_config = [
    '--config=%s/models/mfcc.conf' % basedir,
    '--verbose=0', '--max-mem=10000000000', '--lat-lm-scale=15', '--beam=12.0',
    '--lattice-beam=6.0', '--max-active=5000',
    '%s/models/tri2b_bmmi.mdl' % basedir,
    '%s/models/HCLG_tri2b_bmmi.fst' % basedir,
    '1:2:3:4:5:6:7:8:9:10:11:12:13:14:15:16:17:18:19:20:21:22:23:24:25',
    '%s//models/tri2b_bmmi.mat' % basedir
]
