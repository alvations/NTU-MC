# -*- coding: utf-8 -*-

import os, io, subprocess, time
import sys; reload(sys); sys.setdefaultencoding('utf-8')

class Postech():
    def __init__(self, sejong_dir= '/home/alvas/git/NTU-MC/ntumc/external/sejong/'):
        self.sejong_dir = sejong_dir
    
    def utf8_to_euck(self, text):
        text = unicode(text.decode('utf-8'))
        text = text.replace(u'\xa0', u' ')
        text = text.replace(u'\xe7', u'c') # ç -> c
        text = text.replace(u'\xe9', u'e') # é -> e
        text = text.replace(u'\u2013', u'-') # – -> -
        text = text.replace(u'\xa9', '(c)') # © -> (c)
        return text.encode('euc-kr').strip()
    
    def sejong(self, text):
        text = self.utf8_to_euck(text)
        sejong_dir = self.sejong_dir
        with io.open(sejong_dir+'input.txt', 'wb') as fout:
            fout.write(text)
        
        cmd = "".join(['wine start /Unix ', sejong_dir,'sjTaggerInteg.exe'])
        os.popen(cmd)
        time.sleep(2)
        
        with io.open(sejong_dir+'output.txt', 'r', encoding='euc-kr') as fin:
            sejongtext = fin.read().strip().encode('utf8').decode('utf8')
        
        return sejongtext

    def tokenize(self, text):
        sejongtext = self.sejong(text)
        text = " ".join([i.split(r'/')[0] for i in sejongtext.split()])
        return text
    
    def pos_tag(self, text):
        if isinstance(x, list):
            text = " ".join(text)
        sejongtext = self.sejong(text)
        tagged_text = [tuple(i.split(r'/')) for i in sejongtext.split()]
        return tagged_text
        
    