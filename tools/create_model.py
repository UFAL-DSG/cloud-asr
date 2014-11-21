import argparse
import os
import sys
import tempfile

import lm.build_cloudasr


def require_kaldi():
    """Test whether KALDI_PATH is available in PATH, try to import it from env
    variable and exit the program in case there are problems with it."""

    if not 'KALDI_PATH' in os.environ:
        print 'KALDI_PATH not found. Set KALDI_PATH environment variable to ' \
              'the path with KALDI compiled source.'
        exit(1)


def build_hclg(kaldi_path, am_model, am_tree, am_mfcc, am_mat, am_sil, lm_dict,
               lm_vocab,
               lm_arpa, hclg_out_dir, am_oov):
    temp_dir = tempfile.mkdtemp()
    temp_dir2 = tempfile.mkdtemp()

    params = {
        'kaldi_path': kaldi_path,
        'am_model': os.path.abspath(am_model),
        'am_tree': os.path.abspath(am_tree),
        'am_mfcc': os.path.abspath(am_mfcc),
        'am_mat': os.path.abspath(am_mat),
        'am_sil': os.path.abspath(am_sil),
        'am_oov': am_oov,
        'lm_dict': os.path.abspath(lm_dict),
        'lm_vocab': os.path.abspath(lm_vocab),
        'lm_arpa': os.path.abspath(lm_arpa),
        'tmp_dir': temp_dir,
        'tmp_dir2': temp_dir2,
        'out_dir': os.path.abspath(hclg_out_dir),

    }

    os.system('cd hclg; KALDI_ROOT="{kaldi_path}" bash build_hclg.sh "{'
              'am_model}" "{'
              'am_tree}" '
              '"{am_mfcc}" "{am_mat}" "{am_sil}" '
              '"{lm_dict}" "{lm_vocab}" "{lm_arpa}" "{tmp_dir}" '
              '"{tmp_dir2}" "{out_dir}" "{am_oov}"'.format(**params))


def main(input_text, vocab_size, hclg_out_dir, am_model, am_tree, am_mfcc,
         am_mat, am_sil, am_oov):
    require_kaldi()

    lmb = lm.build_cloudasr.LMBuilderCzech(0)
    lm_file, lm_vocab, lm_dict = lmb.run(input_text, top_n=vocab_size)

    if not os.path.exists(hclg_out_dir):
        os.mkdir(hclg_out_dir)

    kaldi_path = os.environ['KALDI_PATH']
    build_hclg(kaldi_path, am_model, am_tree, am_mfcc, am_mat, am_sil, lm_dict,
               lm_vocab, lm_file, hclg_out_dir, am_oov)


def main_hclg(lm_file, lm_vocab, lm_dict, hclg_out_dir, am_model, am_tree,
              am_mfcc,
         am_mat, am_sil, am_oov):
    require_kaldi()

    if not os.path.exists(hclg_out_dir):
        os.mkdir(hclg_out_dir)

    kaldi_path = os.environ['KALDI_PATH']
    build_hclg(kaldi_path, am_model, am_tree, am_mfcc, am_mat, am_sil, lm_dict,
               lm_vocab, lm_file, hclg_out_dir, am_oov)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_text')
    parser.add_argument('--vocab_size', type=int)
    parser.add_argument('--lm_arpa')
    parser.add_argument('--lm_vocab')
    parser.add_argument('--lm_dict')
    parser.add_argument('hclg_out_dir')
    parser.add_argument('am_model')
    parser.add_argument('am_tree')
    parser.add_argument('am_mfcc')
    parser.add_argument('am_mat')
    parser.add_argument('am_sil')
    parser.add_argument('am_oov')
    args = parser.parse_args()

    if 'input_text' in args:
        main(
            args.input_text,
            args.vocab_size,
            args.hclg_out_dir,
            args.am_model,
            args.am_tree,
            args.am_mfcc,
            args.am_mat,
            args.am_sil,
            args.am_oov
        )
    else:
        main_hclg(
            args.lm_arpa,
            args.lm_vocab,
            args.lm_dict,
            args.hclg_out_dir,
            args.am_model,
            args.am_tree,
            args.am_mfcc,
            args.am_mat,
            args.am_sil,
            args.am_oov
        )