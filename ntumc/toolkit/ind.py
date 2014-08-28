# -*- coding: utf-8 -*-

import os, io, subprocess
import sys; reload(sys); sys.setdefaultencoding('utf-8')

from nltk import word_tokenize

class Indotag():
    def __init__(self):
        self.crf_dir = '/home/alvas/git/NTU-MC/ntumc/external/CRF++-0.58/crf_test'
    def tokenize(self, text):
        return word_tokenize(text)
    def pos_tag(self, text):
        if isinstance(text, list):
            text = " ".join(text).strip()
        # Write to text to temp file.
        os.popen("".join(['echo "', text, '" > tmp.txt']))
        os.popen("sed '$ !s/$/\\n/;s/ /\\n/g' tmp.txt > tmp.crf.txt")
        return [tuple(line.strip().split('\t')) for line in 
                os.popen(" ".join([self.crf_dir, 
                                   '-m model.id tmp.crf.txt'])).readlines()]