#!/usr/bin/env python
# encoding: utf8

import os
import wget

import phonetic_transcription

def download_general_LM_data(language):
    """Download a general text corpus for the specified language.

    :param language: abbreviation of teh desired language. It can be either
           in ISO 639/1 or 639/3
    :return: File name of the downloaded data.
    """
    lngs = {'eng': 'eng',
            'en':  'eng',
            'ces': 'ces',
            'cs':  'ces',
            'fra': 'fra',
            'fr':  'fra',
            'spa': 'spa',
            'sp':  'spa',
            'ita': 'ita',
            'it':  'ita',
            'deu': 'ita',
            'de':  'ita',
            }

    if os.path.exists("%s.txt.gz" % lngs[language]):
        return "%s.txt.gz" % lngs[language]
    elif language in lngs:
        url = "https://ufal-point.mff.cuni.cz/repository/xmlui/bitstream/" \
              "handle/11858/00-097C-0000-0022-6133-9/%s.txt.gz" % lngs[language]
        fn = wget.download(url)
        print
        return fn

    raise Exception("Missing a supported language name:")


def is_srilm_available():
    """Test whether SRILM is available in PATH."""
    return os.system("which ngram-count") == 0

def run(cmd, msg=None):
    """Run command and raise exception when it fails (returns non-zero code)."""
    print cmd
    system_res = os.system(cmd)
    if not system_res == 0:
        err_msg = "Command failed, exitting."
        if msg:
            err_msg = "%s %s" % (err_msg, msg, )
        raise Exception(err_msg)



def require_srilm():
    """Test whether SRILM is available in PATH, try to import it from env
    variable and exit the program in case there are problems with it."""
    if not is_srilm_available():
        if 'SRILM_PATH' in os.environ:
            srilm_path = os.environ['SRILM_PATH']
            os.environ['PATH'] += ':%s' % srilm_path
            if not is_srilm_available():
                print 'SRILM_PATH you specified does not contain the ' \
                      'utilities needed. Please make sure you point to the ' \
                      'directory with the SRILM binaries.'
                exit(1)

        else:
            print 'SRILM not found. Set SRILM_PATH environment variable to ' \
                  'the path with SRILM binaries.'
            exit(1)


class LMBuilder(object):
    allowed_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    phon_transcr_class = None

    def __init__(self, begin_step):
        self.begin_step = begin_step
        self.curr_step = 0
        self.phon_transcr = self.phon_transcr_class

        # Test if SRILM is available.
        require_srilm()

    def run(self, input_data, vocab_file=None, top_n=None):
        # Normalize the input text data.
        norm_data_file = self.normalize(input_data,
                                        pretend=self.should_skip_this())
        self.next_step()

        if top_n and vocab_file:
            raise Exception('Parameters top_n and vocab_file are not '
                            'compatible.')
        elif top_n:
            words = self.sort_words_by_freq(norm_data_file)
            vocab = self.head(words, top_n)
        else:
            vocab = vocab_file

        # Build LM.
        lm_vocab, output_1counts_file, lm = (
            self.train_lm(norm_data_file, vocab)
        )
        self.next_step()

        # Prune LM.
        lm = self.prune_lm(2, lm)
        self.next_step()

        # Add some auxiliary things to vocabulary.
        lm_vocab = self.finalize_vocab(lm_vocab)
        self.next_step()

        # Build the dict.
        lm_dict = self.build_dict(lm_vocab)

        print lm, lm_vocab, lm_dict

    def should_skip_this(self):
        return self.curr_step < self.begin_step

    def next_step(self):
        self.curr_step += 1

    def prefix(self, name):
        return "%.2d_%s" % (self.curr_step, name)

    def normalize(self, input_file, pretend=False):
        output_file = self.prefix("normalize.gz")
        cmd = (r"zcat %s "
               r"| iconv -f UTF-8 -t UTF-8//IGNORE "
               r"| sed 's/\. /\n/g' "
               r"| sed 's/"
               r"[[:digit:]]/ /g; s/[^[:alnum:]]/ /g; s/[ˇ]/ /g; s/ \+/ /g' "
               r"| sed 's/[[:lower:]]*/\U&/g' "
               r"| grep -E '^[%s ]*$'"
               r"| sed s/[\%s→€…│]//g "
               r"| gzip > %s" % (input_file, self.allowed_letters, "'",
                                 output_file)
        )

        if not pretend:
            run(cmd)

        return output_file

    def sort_words_by_freq(self, f_name):
        out_file = self.prefix("sort_words_by_freq.txt")
        cmd = "zcat %s | tr ' ' '\n' | sort | uniq -c | sort -n -r | \
                                   cut -b 9- > %s" % (f_name, out_file)

        run(cmd)

        return out_file

    def head(self, f_name, n):
        out_file = self.prefix("head.txt")
        cmd = "head -n %d %s > %s" % (n, f_name, out_file)

        run(cmd)

        return out_file

    def train_lm(self, input_text_file, input_vocab_file=None):
        output_vocab_file = self.prefix("train_lm_vocab.txt")
        output_1counts_file = self.prefix("train_lm_1counts.txt")
        output_arpa_file = self.prefix("train_lm.arpa")

        cmd = ("ngram-count -text %s %s -limit-vocab -write-vocab %s "
               "-write1 %s -order 2 -wbdiscount -memuse -lm %s" %
                  (input_text_file,
                   "-vocab %s" % input_vocab_file if input_vocab_file else "",
                   output_vocab_file,
                   output_1counts_file,
                   output_arpa_file)
        )

        run(cmd)

        return (output_vocab_file, output_1counts_file, output_arpa_file)

    def prune_lm(self, order, input_lm_file):
        output_lm_file = self.prefix("prune_lm.arpa")
        cmd = "ngram -lm %s -order %d -write-lm %s -prune-lowprobs -prune " \
              "0.0000001 -renorm" \
                  % (input_lm_file, order, output_lm_file)

        run(cmd)

        return output_lm_file

    def finalize_vocab(self, input_vocab_file):
        output_vocab_file = self.prefix("finalize_vocab.txt")
        filter_out = [
            "\-pau\-",
            "<s>",
            "</s>",
            "<unk>",
            "CL_",
            "{",
            "_INHALE_",
            "_LAUGH_",
            "_EHM_HMM_",
            "_NOISE_",
        ]

        cmd = "cat %s | grep -vE '%s' > %s" % \
                  (input_vocab_file,
                   "|".join(filter_out),
                   output_vocab_file)

        run(cmd)

        return output_vocab_file


    def build_dict(self, vocab_file):
        lm_dict = self.prefix("build_dict.txt")
        self.phon_transcr.run(vocab_file, lm_dict)

        return lm_dict


class LMBuilderCzech(LMBuilder):
    allowed_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZÁČĎĚÍŇÓŘŠŤÚŮÝŽ"
    phon_transcr_class = phonetic_transcription.PTranscriptionCS


class LMBuilderEnglish(LMBuilder):
    allowed_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    phon_transcr_class = phonetic_transcription.PTranscriptionEN


if __name__ == '__main__':
    lmb = LMBuilder(0)
    lmb.run(download_general_LM_data('cs'), "vocab50k.filtered.txt")
    lmb.run(download_general_LM_data('en'), "en_vocab50k.filtered.txt")
