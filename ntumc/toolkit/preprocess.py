# -*- coding: utf-8 -*-

import os, io, subprocess, time
import sys; reload(sys); sys.setdefaultencoding('utf-8')

from nltk.tokenize import word_tokenize
from nltk import pos_tag as nltk_pos_tag

import cmn, kor, jpn, vie

chinese = cmn.StanfordNLP()
korean = kor.Postech()
japanese = jpn.Mecab()
vietnamese = vie.Jvntextpro()

lang2lib = {'jpn':japanese, 'cmn':chinese, 
            'vie':vietnamese, 'kor':korean}

def tokenize(text, lang):
    if lang in ['eng', 'ind']:
        return " ".join(word_tokenize(text))
    elif lang in lang2lib:
        return lang2lib[lang].tokenize(text)
    else:
        return " ".join(text.split())
        
def pos_tag(text, lang):
    if lang == 'eng':
        return nltk_pos_tag(word_tokenize(text))
    if lang in lang2lib:
        return lang2lib[lang].pos_tag(text)
    