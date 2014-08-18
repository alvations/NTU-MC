# -*- coding: utf-8 -*-

import os, io, subprocess
import sys; reload(sys); sys.setdefaultencoding('utf-8')

class Jvntextpro():
    def __init__(self, jvn_dir='/home/alvas/JVnTextPro-v.2.0/'):
        self.jvn_dir = jvn_dir
    
        self.segmenter_cmd = "".join(['java -mx512M -cp ',
                                       jvn_dir, '/bin:', 
                                       jvn_dir + '/libs/args4j.jar:',
                                       jvn_dir + '/libs/lbfgs.jar ',
                                       'jvnsegmenter.WordSegmenting ',
                                       '-modeldir ', jvn_dir, 
                                       '/models/jvnsegmenter ',
                                       '-inputfile tmp.txt',
                                       ' -outputfile tmp.txt.wseg'])
        
    def tokenize(self, text):
        # Write to text to temp file.
        os.popen("".join(['echo "', text, '" > tmp.txt']))
        # Runs segmenter.
        os.popen(self.segmenter_cmd)
        # Reads from output file.
        text = io.open('tmp.txt.wseg', 'r', encoding='utf8').read().strip()
        return text