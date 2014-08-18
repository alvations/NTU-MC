# -*- coding: utf-8 -*-

import os, io, subprocess
import sys; reload(sys); sys.setdefaultencoding('utf-8')

class StanfordNLP():
    def __init__(self, stanford_dir='/home/alvas/stanford-segmenter-2014-06-16'):
        self.stanford_dir = stanford_dir
    
        self.segmenter_cmd = " ".join(["bash",stanford_dir+'/segment.sh',
                                  "ctb tmp.txt UTF8 0"])
    
    
    def tokenize(self, text):
        # Write to text to temp file.
        os.popen("".join(['echo "', text, '" > tmp.txt']))
        # Runs the segmenter.
        text, err = subprocess.Popen(self.segmenter_cmd,
                        shell = True, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE).communicate()
        # Reads from subprocess output.
        text = text.decode().strip()
        return text