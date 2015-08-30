#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import argparse
import os
from subprocess import Popen, PIPE
from os import environ
from os.path import abspath, dirname, join
import sys
import shutil
from collections import defaultdict
from tempfile import NamedTemporaryFile


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


def backup_build_models(args_dict):
    print >> sys.stderr, "\nCopying required files to target directory %s\n" % output_dir
    out_dir = args_dict['out_dir']
    for f in ['model', 'conf', 'mat']:
        shutil.copyfile(args_dict[f], out_dir)
    shutil.copyfile(join(args_dict['tmp_dir'], 'hclg', 'HCLG.fst'), out_dir)
    shutil.copyfile(join(args_dict['tmp_dir'], 'lang', 'words.txt'), out_dir)
    shutil.copyfile(join(args_dict['tmp_dir'], 'lang', 'phones', 'silence.csl'), out_dir)
    shutil.copyfile(join(args_dict['tmp_dir'], 'dict',  'lexicon.txt'), out_dir)

    shutil.copyfile(join(args_dict['tmp_dir'], 'dict',  'lexicon.txt'), out_dir)
    shutil.copyfile(join(args_dict['tmp_dir'], 'dict',  'silence_phones.txt'), out_dir)
    shutil.copyfile(join(args_dict['tmp_dir'], 'dict',  'optional_silence.txt'), out_dir)
    shutil.copyfile(join(args_dict['tmp_dir'], 'dict',  'extra_questions.txt'), out_dir)


def exit_on_system_fail(cmd, msg=None):
    # FIXME print sys.stderr output
    system_res = os.system(cmd)
    if not system_res == 0:
        err_msg = "Command '%s' failed, exiting." % cmd
        if msg:
            err_msg = "%s %s" % (err_msg, msg, )
        raise RuntimeError(err_msg)


def load_dict(arg_dict):
    # FIXME lang_id unused
    filename = arg_dict['phon_dict']
    d = defaultdict(set)
    with open(filename, 'r') as r:
        for line in r:
            word, phon_trans = line.split(' ', 1)
            phon_trans = phon_trans.strip()
            d[word].add(phon_trans)
    return filename, d


def build_dict(arg_dict, exclude_words=None):
    arpa, lang_id = arg_dict['lm'], arg_dict['lang']
    if exclude_words is None:
        exclude_words = ['<s>', '</s>']
    exclude_words = set(exclude_words)

    vocab = set()
    with open(arpa, 'r') as r:
        unigrams = False
        for line in r:
            if line.strip() == '\\1-grams:':
                unigrams = True
                continue
            if line.strip() == '' and unigrams:
                unigrams = False
                break
            if unigrams:
                word = line.split()[1]
                vocab.add(word)
    vocab = vocab.difference(exclude_words)
    print 'DEBUG 0', len(vocab)

    kams_root = environ['KAMS_ROOT']
    if os.path.isfile(join(kams_root, 'kams', 'local', 'prepare_%s_transcription.sh' % lang_id)):
        print >> sys.stderr, "Using selected mapping '%s' for creating phonetic dictionary from arpa file %s" % (lang_id, arpa)
    else:
        lang_id = 'dummy'
        print >> sys.stderr, "Selected mapping %s for creating phonetic dictionary NOT FOUND! Using dummy transcription!" % lang_id
    phonetic_trans_script = join(kams_root, 'kams', 'local', 'prepare_%s_transcription.sh' % lang_id)

    vocab_file = NamedTemporaryFile(prefix=os.path.basename(arpa), suffix='vocab', delete=False)
    phon_dict_file = NamedTemporaryFile(prefix=os.path.basename(arpa), suffix='dict', delete=False)

    with open(vocab_file.name, 'w') as wv:
        with open(phon_dict_file.name, 'w') as wd:
            wv.write('\n'.join(vocab))
            exit_on_system_fail('%s %s %s' % (phonetic_trans_script, vocab_file.name, phon_dict_file.name))
            return phon_dict_file.name, load_dict(phon_dict_file.name)


def extract_alphabet(phonetic_dict):
    alphabet = set()
    for prons in phonetic_dict.itervalues():
        for pron in prons:
            chars = set(pron.strip().split(' '))
            alphabet.union(chars)
    return alphabet


def extract_vocabulary(phonetic_dict):
    return phonetic_dict.keys()
