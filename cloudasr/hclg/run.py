#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import argparse
import os
from subprocess import Popen, PIPE
from os import environ


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
        raise Exception(err_msg)


if __name__ == '__main__':
    path_sh = '/kaldi_uproot/kams/kams/path.sh'
    parser = argparse.ArgumentParser(description='Build HCLG graph for Kaldi')
    parser.add_argument('--path-sh', help='shell script updating PATH to include IRSTLM and Kaldi binaries', default=path_sh)

    args = parser.parse_args()
    path_sh = args.path_sh

    env = source(path_sh)
    exit_on_system_fail("echo $PATH")
    exit_on_system_fail("echo $IRSTLM")


    exit_on_system_fail("lattice-oracle --help")
    # exit_on_system_fail("build-lm.sh")
    # exit_on_system_fail("touch test; echo $?")
    time.sleep(1.0)
