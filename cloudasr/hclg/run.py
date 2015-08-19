#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import argparse
import os
from subprocess import Popen, PIPE
from os import environ
import sys


def source(script, update=True, clean=False):
    """
    Source variables from a shell script
    import them in the environment (if update==True)
    and report only the script variables (if clean==True)
    Based on: https://gist.github.com/mammadori/3891614
    """

    global environ
    if clean:
        environ_back = dict(environ)
        environ.clear()

    pipe = Popen(". %s; printenv" % script, stdout=PIPE, shell=True)
    data = pipe.communicate()[0]
    if pipe.returncode != 0:
        raise ValueError("Script %s was not sourced succesfully:\n%s\n" % (script, data))

    env = dict((line.split("=", 1) for line in data.splitlines()))

    if clean:
        # remove unwanted minimal vars
        env.pop('LINES', None)
        env.pop('COLUMNS', None)
        environ = dict(environ_back)

    if update:
        environ.update(env)
    return env


def exit_on_system_fail(cmd, msg=None):
    system_res = os.system(cmd)
    if not system_res == 0:
        err_msg = "Command failed, exitting."
        if msg:
            err_msg = "%s %s" % (err_msg, msg, )
        raise RuntimeError(err_msg)


def load_dict(args):
    print 'TODO copy dict'


def build_dict(args):
    print 'TODO phonetic dictionary from LM and language id'


def extract_alphabet(phonetic_dict):
    pass


def extract_vocabulary(phonetic_dict):
    pass



if __name__ == '__main__':
    try:
        exit_on_system_fail("lattice-oracle --help")
    except RuntimeError:
        print >> sys.stderr, "Kaldi binaries not available"
        exit_on_system_fail("echo $PATH")
        exit 1

    parser = argparse.ArgumentParser(description='Build HCLG graph for Kaldi')
    parser.add_argument('--path-sh', help='shell script updating PATH to include IRSTLM and Kaldi binaries', default='/kaldi_uproot/kams/kams/path.sh')
    parser.add_argument('--lm', help='LM in arpa format', required=True)
    parser.add_argument('-oov', '--out-of-vocabulary', default='<UNK>')
    parser.add_argument('-tmp', '--tmp-directory', default=os.path.abspath(os.path.dirname(__file__)))

    # TODO supporting only tri2b
    am_group = parser.add_argument_group('AM training files')
    am_group.add_argument('-am', help='Acoustic model - typically you want final.mdl from Kaldi training scripts.', required=True)
    am_group.add_argument('-config', help='Configuration file which should store all non-default values used for acoustic signal preprocessing and AM parameters which needs to be the same during decoding.', required=True)
    am_group.add_argument('-tree', help='Tree for tying GMM - Gaussian Mixture Models.', required=True)
    am_group.add_argument('-trans-matrix', help='Matrix for linear transformation e.g. lda+mllt.', required=True)
    am_group.add_argument('-sil', '--silence-phones-ids', required=True)  # TODO use them more


    subparses = parser.add_subparsers()
    load_dict_parser = subparser.add_parser('load_dict')
    load_dict_parser.add_argument('-f', required=True, help='Path to phonetic dictionary')
    load_dict_parser.set_defaults(prepare_lm_dict=load_dict)

    build_dict_parser = subparser.add_parser('build_dict')
    build_dict_parser.add_argument('--lang', choices=['cs', 'en'])
    build_dict_parser.set_defaults(prepare_lm_dict=build_dict)

    args = parser.parse_args()

    lm_dict = args.prepare_dict(args)
    am_dict = load_dict(args.am_dict)
    phonetic_alphabet_lm = extract_alphabet(lm_dict)
    phonetic_alphabet_am = extract_alphabet(am_dict)

    # Check phonetic alphabets are exactly the same
    assert len(phonetic_alphabet_am) == len(phonetic_alphabet_lm) and len([x for x in phonetic_alphabet_am if x not in phonetic_alphabet_lm]) == 0

    common_keys = set(lm_dict.keys()) & set(am_dict.keys())
    diff_pronunciation = [am_dict[c], lm_dict[c] for c in common_keys if am_dict[c] != lm_dict[c]]
    if len(diff_pronunciation) == 0:
        print >> sys.stderr, "Phonetic dictionaries are the same"
    for a, b in diff_pronunciation:
        print >> sys.stderr, "Phonetic dictionary differs:  %s vs %s" % (a, b)


    env = source(args.path_sh)

    exit_on_system_fail("./kaldi_build_hclg.sh %(model)s %(tree)s %(conf)s %(mat)s %(sil)s %(dictionary)s %(vocabulary)s %(lm_arpa)s %(oov)s %(tmpdir)s %(out_dir)s" % vars(args))

    # TODO rewrite more from kaldi_build_hclg.sh to Python
