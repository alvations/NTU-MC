# -*- coding: utf-8 -*-

import os, io, subprocess, time
import sys; reload(sys); sys.setdefaultencoding('utf-8')

from preprocess import tokenize, pos_tag

def text2naf(text, sentid, paraid):
    """
    <wf id="w1" offset="0" length="4" sent="1" para="1">John</wf>
    """
    textnaf = []
    textnaf.append('<text>')
    stridx = 0
    for wid, word in enumerate(text.split()):
       line = '\t<wf id="w'+str(wid)+ '" offset="'+str(stridx)
       line+= '" length="'+str(len(word))+ '" sent="'+str(sentid)
       line+= '" para="'+str(paraid)+'">'+word+'''</wf>'''
       textnaf.append(line)
    textnaf.append(r'<\text>')
    return "\n".join(textnaf)

indir = '/home/alvas/git/NTU-MC/ntumc-v5/subcorpora/yoursing/cleanest/'
langs = os.walk(indir).next()[1]

for lang in langs:
    langdir = indir+lang+'/'
    for filename in os.walk(langdir).next()[2]:
        if filename.endswith('~'):
            continue
        textxml_header = "".join(['<text xml:lang="', lang,'">'])
        ##print textxml_header
        webpage = ''
        title = ''
        for line in io.open(langdir+filename, 'r', encoding='utf8'):
            line = line.strip()
            if line.startswith('#M'):
                webpage = line.split('\t')[1]
            elif line.startswith('#T'):
                text = line.split('\t')[1]
            elif line.startswith('#H'):
                text = line.split('\t')[1]
                header = True
                header_index = int(line.split('\t')[0][2:])
                ##print header, header_index, text
            elif line.startswith("#P"):
                idx, text = line.split('\t')
                paraid, sentid = idx.split()
                paraid = int(paraid.split('\t')[0][2:])
                sentid = int(sentid.split('\t')[0][2:])
                ##text = tokenize(text, lang)
                ##print text2naf(text, sentid, paraid)
                
                tagged_text = pos_tag(text, lang)
                tokens, tags = zip(*tagged_text)
                
                print text2naf(" ".join(tokens), sentid, paraid)
                