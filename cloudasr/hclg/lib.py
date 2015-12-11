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
import logging


logger = logging.getLogger(__name__)


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

    pipe = Popen(". %s && printenv" % script, stdout=PIPE, shell=True)
    data = pipe.communicate()[0]
    if pipe.returncode != 0:
        raise ValueError("Script %s was not sourced succesfully:\n%s\n" % (script, data))

    env = {}
    for line in data.splitlines():
        try:
            k, v = line.split("=", 1)
            env[k] = v
        except:
            logger.warning("Line from file %s was not succesfully sourced:\n%s\n", script, line)
            continue

    if clean:
        # remove unwanted minimal vars
        env.pop('LINES', None)
        env.pop('COLUMNS', None)
        environ = dict(environ_back)

    if update:
        environ.update(env)
    return env


def backup_build_models(args_dict):
    out_dir = args_dict['out_dir']
    logger.info("\nCopying required files to target directory %s\n", out_dir)
    for f in ['am', 'conf', 'mat']:
        shutil.copy2(args_dict[f], out_dir)
    shutil.copy2(join(args_dict['tmp_directory'], 'hclg', 'HCLG.fst'), out_dir)
    shutil.copy2(join(args_dict['tmp_directory'], 'lang', 'words.txt'), out_dir)
    shutil.copy2(join(args_dict['tmp_directory'], 'lang', 'phones', 'silence.csl'), out_dir)
    shutil.copy2(join(args_dict['tmp_directory'], 'dict',  'lexicon.txt'), out_dir)

    shutil.copy2(join(args_dict['tmp_directory'], 'dict',  'silence_phones.txt'), out_dir)
    shutil.copy2(join(args_dict['tmp_directory'], 'dict',  'optional_silence.txt'), out_dir)
    shutil.copy2(join(args_dict['tmp_directory'], 'dict',  'extra_questions.txt'), out_dir)


def exit_on_system_fail(cmd, msg=None):
    logger.debug("Running cmd:\n%s\n", cmd)
    system_res = os.system(cmd)
    if not system_res == 0:
        err_msg = "Command '%s' failed, exiting." % cmd
        if msg:
            err_msg = "%s %s" % (err_msg, msg, )
        raise RuntimeError(err_msg)


def load_dict(dict_file, intact_symbols):
    d = defaultdict(set)
    with open(dict_file, 'r') as r:
        for line in r:
            word, phon_trans = line.split(' ', 1)
            phon_trans = phon_trans.strip()
            d[word].add(phon_trans)
    intact_in_dict = set(d.keys()) & set(intact_symbols)
    assert intact_in_dict == set(intact_symbols), "Intact symbols e.g. noise symbols required to be present in the dictionary: %s vs required %s" % (intact_in_dict, intact_symbols)
    return dict_file, d


def build_dict(arg_dict, intact_symbols, exclude_words=None):
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
    vocab = vocab.difference(intact_symbols)

    kams_root = environ['KAMS_ROOT']
    if os.path.isfile(join(kams_root, 'kams', 'local', 'prepare_%s_transcription.sh' % lang_id)):
        logger.info("Using selected mapping '%s' for creating phonetic dictionary from arpa file %s", lang_id, arpa)
    else:
        lang_id = 'dummy'
        logger.warning("Selected mapping %s for creating phonetic dictionary NOT FOUND! Using dummy transcription!", lang_id)
    phonetic_trans_script = join(kams_root, 'kams', 'local', 'prepare_%s_transcription.sh' % lang_id)

    vocab_file = NamedTemporaryFile(prefix=os.path.basename(arpa), suffix='vocab', delete=True)
    phon_dict_file = NamedTemporaryFile(prefix=os.path.basename(arpa), suffix='dict', delete=False)

    with open(vocab_file.name, 'w') as wv:
        with open(phon_dict_file.name, 'w') as wd:
            wv.write('\n'.join(vocab))
            exit_on_system_fail('%s %s %s' % (phonetic_trans_script, vocab_file.name, phon_dict_file.name))

    logger.debug("Inserting missing intact symbols to %s", phon_dict_file.name)
    with open(phon_dict_file.name, 'a') as wd:
        for s in intact_symbols:
            logger.debug("appending special symbol %s to dictionary", s)
            wd.write('%s       %s\n' % (s, s))
    _, d = load_dict(phon_dict_file.name, [])
    return phon_dict_file.name, d


def extract_alphabet(phonetic_dict):
    alphabet = set()
    for prons in phonetic_dict.itervalues():
        for pron in prons:
            chars = set(pron.strip().split(' '))
            alphabet.union(chars)
    return alphabet


def extract_vocabulary(phonetic_dict):
    return phonetic_dict.keys()
