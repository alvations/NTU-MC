# -*- coding: utf-8 -*-

import os, io, subprocess
import sys; reload(sys); sys.setdefaultencoding('utf-8')

class StanfordNLP():
    def __init__(self, 
                 stanford_segdir='/home/alvas/stanford-segmenter-2014-06-16',
                 stanford_posdir='/home/alvas/stanford-postagger-full-2014-06-16'):
        self.stanford_segdir = stanford_segdir
        self.segmenter_cmd = " ".join(["bash",stanford_segdir+'/segment.sh',
                                  "ctb tmp.txt UTF8 0"])
        
        self.stanford_posdir = stanford_posdir
        
        self.tagger_cmd = " ".join(['java', '-cp', 
                                    stanford_posdir+'/stanford-postagger.jar',
                                    'edu.stanford.nlp.tagger.maxent.MaxentTagger',
                                    '-model', stanford_posdir+'/models/chinese-nodistsim.tagger',
                                    '-textFile tmp.txt'])
                
    
    def tokenize(self, text, batch=False):
        # Write to text to temp file.
        if batch:
            os.popen("".join(['echo -e "', '\n'.join(text), '" > tmp.txt']))
        else:
            os.popen("".join(['echo "', text, '" > tmp.txt']))
        # Runs the segmenter.
        text, err = subprocess.Popen(self.segmenter_cmd,
                        shell = True, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE).communicate()
        # Reads from subprocess output.
        text = text.decode('utf8').strip()
        if batch:
            return [i.strip().split() for i in text.split('\n')]
        else:
            return text.split()
    
        
    def pos_tag(self, text, batch=False):
        if batch:
            text = [' '.join(i) if isinstance(i, list) else i for i in text]
            os.popen("".join(['echo -e "', '\n'.join(text), '" > tmp.txt']))
        else:
            if isinstance(text, list):
                text = " ".join(text)
            # Write to text to temp file.
            os.popen("".join(['echo "', text, '" > tmp.txt']))
        # Runs the tagger.
        text, err = subprocess.Popen(self.tagger_cmd,
                        shell = True, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE).communicate()
        # Reads from subprocess output.
        text = text.decode('utf8').strip()
        if batch:
            return [[tuple(i.split(r'#')) for i in t.split()] 
                    for t in text.split('\n')] 
        else:
            return [tuple(i.split(r'#')) for i in text.decode('utf8').split()]
    
    