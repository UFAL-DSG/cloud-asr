import sys
from cloudam import CloudAM


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--out_cloudam')
    parser.add_argument('--kaldi_model')
    parser.add_argument('--kaldi_tree')
    parser.add_argument('--kaldi_mat')
    parser.add_argument('--kaldi_mfcc')
    parser.add_argument('--kaldi_silence')
    parser.add_argument('--kaldi_oov')
    args = parser.parse_args()

    if not all([args.out_cloudam, args.kaldi_model, args.kaldi_tree,
            args.kaldi_mat, args.kaldi_mfcc, args.kaldi_silence,]):
        print >>sys.stderr, "Error: Missing arguments."
        parser.print_help()
        exit(1)

    CloudAM.build_from_kaldi(
        args.out_cloudam,
        args.kaldi_model,
        args.kaldi_tree,
        args.kaldi_mfcc,
        args.kaldi_mat,
        args.kaldi_silence,
        args.kaldi_oov
    )


if __name__ == '__main__':
    main()