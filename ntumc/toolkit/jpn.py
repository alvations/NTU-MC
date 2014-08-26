# -*- coding: utf-8 -*-

import os, io, subprocess
import sys; reload(sys); sys.setdefaultencoding('utf-8')

from operator import itemgetter

class Mecab():
    def __init__(self):
        pass
    def tokenize(self, text):
        cmd = unicode("".join(['echo "', text.decode('utf8'),
                       '" | mecab -O wakati']))
        return os.popen(cmd).read().strip().split()
    
    def pos_tag(self, text):
        if text.count(' ') == 0:
            text = self.tokenize(text)
        text = " ".join(text)
        cmd = unicode("".join(['echo "', text.decode('utf8'),
                       '" | mecab -Ochasen']))
        return [itemgetter(0,3)(unicode(i.strip()).split()) 
                for i in os.popen(cmd).readlines()[:-1]]