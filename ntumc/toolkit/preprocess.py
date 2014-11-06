# -*- coding: utf-8 -*-

import os, io, subprocess, time
import sys; reload(sys); sys.setdefaultencoding('utf-8')

from nltk.tokenize import word_tokenize
from nltk import pos_tag as nltk_pos_tag

import cmn, kor, jpn, vie, ind

chinese = cmn.StanfordNLP()
korean = kor.Postech()
japanese = jpn.Mecab()
vietnamese = vie.Jvntextpro()
indonesian = ind.Indotag()

lang2lib = {'jpn':japanese, 'cmn':chinese, 
            'vie':vietnamese, 'kor':korean,
            'ind':indonesian}

def tokenize(text, lang, batch=False):
    if lang in ['eng', 'ind']:
        return " ".join(word_tokenize(text))
    elif lang in lang2lib:
        return lang2lib[lang].tokenize(text, batch=batch)
    else:
        return text.split()
        
def pos_tag(text, lang, batch=False):
    if lang == 'eng':
        return nltk_pos_tag(word_tokenize(text))
    if lang in lang2lib:
        return lang2lib[lang].pos_tag(text, batch=batch)
