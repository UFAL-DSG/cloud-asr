import StringIO
import json
import sys
import tarfile


class CloudAM(object):
    def __init__(self, file_name):
        pass

    @classmethod
    def build_from_kaldi(cls, out_path, am_model, am_tree, am_mfcc, am_mat, \
                         am_sil, am_oov):
        meta = {
            'oov': am_oov
        }
        meta_txt = json.dumps(meta)
        meta_f = StringIO.StringIO()
        meta_f.write(meta_txt)
        meta_f.seek(0)

        meta_info = tarfile.TarInfo(name="meta")
        meta_info.size = len(meta_f.buf)

        with tarfile.open(out_path, "w") as tar:
            tar.addfile(tarinfo=meta_info, fileobj=meta_f)
            tar.add(am_model, "model")
            tar.add(am_tree, "tree")
            tar.add(am_mfcc, "mfcc")
            tar.add(am_mat, "mat")
            tar.add(am_sil, "am_sil")


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