# encoding: utf8
from collections import defaultdict
import json
import os
import re
import sys


def perl_to_regexp(text):
    res = []
    for ln in text.split('\n'):
        ln = ln.strip()
        if ln.startswith('#'):
            continue
        elif ln.startswith('s/'):
            expr = ln[2:-3]
            expr = expr.replace(r'\@', '@')
            p_from, p_to = expr.split('/', 1)
            p_to = p_to.replace('$', '\\')
            res.append((re.compile(p_from, re.MULTILINE), p_to))
        elif ln == "":
            pass
        else:
            raise Exception('Unknown line: "%s"' % ln)
    return res


class PTranscription:
    def run(self, input_file, output_file):
        with open(input_file) as f_in, open(output_file, 'w') as f_out:
            self.process(f_in, f_out)

    def process(self, f_in, f_out):
        raise NotImplementedError()

    def get_resource(self, f_name):
        return os.path.join(
            os.path.dirname(__file__),
            'phonetic_data',
            f_name
        )


class PTranscriptionCS(PTranscription):
    # List of Perl regular expressions for transforming the input vocabulary to
    # dict.
    # e.g. s/D$/T/g;
    exceptions = None
    transcription = None
    prague2pilsen = None
    infreq = None

    def __init__(self):
        self.deserialize(self.get_resource('cz_data.txt'))

        self.rules_1 = (
            perl_to_regexp(self.exceptions)
            + perl_to_regexp(self.transcription))

        self.rules_2 = (
            perl_to_regexp(self.prague2pilsen)
            + perl_to_regexp(self.infreq))

    def serialize(self, out_file):
        with open(out_file, 'w') as f_out:
            json.dump(
                {
                    'exceptions': self.exceptions,
                    'transcription': self.transcription,
                    'prague2pilsen': self.prague2pilsen,
                    'infreq': self.infreq
                }, f_out)

    def deserialize(self, in_file):
        with open(in_file) as f_in:
            data = json.load(f_in)
            self.exceptions = data['exceptions']
            self.transcription = data['transcription']
            self.prague2pilsen = data['prague2pilsen']
            self.infreq = data['infreq']


    def process(self, f_in, f_out):
        output_text = f_in.read().decode('utf8')

        input_text = output_text

        output_text = output_text.upper()

        for expr, p_to in self.rules_1:
            output_text = expr.sub(p_to, output_text)

        output_text = output_text.lower()

        for expr, p_to in self.rules_2:
            output_text = expr.sub(p_to, output_text)


        for i_word, o_word in zip(input_text.split('\n'),
                                  output_text.split('\n')):
            f_out.write(i_word.encode('utf8')
                        + '       '
                        + o_word.encode('utf8')
                        + '\n')


class PTranscriptionEN(PTranscription):
    def __init__(self):
        self.dict = defaultdict(list)
        with open(self.get_resource('en_dict.txt')) as f_in:
            for ln in f_in:
                word, p_word = ln.strip().split('\t')
                self.dict[word].append(p_word)

    def process(self, f_in, f_out):
        for ln in f_in:
            word_orig = ln.strip()
            word = word_orig.upper()

            for form in self.dict[word]:
                f_out.write(u"%s       %s\n" % (word_orig, form, ))


if __name__ == '__main__':
    PTranscriptionEN().run(sys.argv[1], sys.argv[2])
    PTranscriptionCS().run(sys.argv[1], sys.argv[2])