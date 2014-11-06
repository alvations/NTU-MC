# -*- coding: utf-8 -*-

import os, io, subprocess, time
import sys; reload(sys); sys.setdefaultencoding('utf-8')

from preprocess import tokenize, pos_tag

def text2naf(text, sentid, thisparaid, wordid):
    """
    <wf id="w1" offset="0" length="4" sent="1" para="1">John</wf>
    """
    textnaf = []
    stridx = 0
    for wid, word in enumerate(text.split(), start=1):
       line = '\t<wf id="w'+str(wid+wordid)+ '" offset="'+str(stridx)
       line+= '" length="'+str(len(word))+ '" sent="'+str(sentid)
       line+= '" para="'+str(thisparaid)+'">'+word+'''</wf>'''
       textnaf.append(line)
       stridx+=len(word)+1
    return "\n".join(textnaf), wordid+wid

def term2naf(tokens, tags, wordid):
    termnaf = []
    wid = 1
    for token, tag in zip(tokens, tags):
        line = '\t<term id="t'+str(wid+wordid)+'" pos="'+tag+'">\n'
        line+= '\t\t<span><target id="w'+str(wid+wordid)+'"/></span>\n'
        line+= '\t' + r'<\term>'
        termnaf.append(line)
        wid+=1
    return "\n".join(termnaf)
        
indir = '/home/alvas/git/NTU-MC/ntumc-v5/subcorpora/yoursing/cleanest/'
langs = os.walk(indir).next()[1]

for lang in langs:
    if lang == "eng" or lang == "cmn":
        continue
    langdir = indir+lang+'/'
    fout = io.open('ntumc-'+lang+'.naf', 'wb')
    for filename in sorted(os.walk(langdir).next()[2]):
        if filename.endswith('~'):
            continue        
        webpage = ''
        title = ''
        wordid = 1
        textlayer = []
        textlayer.append('<!-- text layer -->')
        textlayer.append('<text>')
        
        termlayer = []
        termlayer.append('<!-- term layer -->')
        termlayer.append('<terms>')
        
        lines = []
        
        for line in io.open(langdir+filename, 'r', encoding='utf8'):
            line = line.strip()
            if line.startswith('#M'):
                webpage = line.split('\t')[1].replace('<!-- Mirrored from ','')
                webpage = webpage.partition(' ')[0]
            elif line.startswith('#T'):
                text = line.split('\t')[1].replace('YourSingapore.com - ','')
                ##print text
                textxml_header = "".join(['<naf xml:lang="', lang,'"', 
                                          " doc='"+filename,'"',
                                          " url='"+webpage,'"',
                                          " title='"+text,'"',
                                          ">"])
                fout.write(unicode(textxml_header)+"\n")
            elif line.startswith('#H'):
                ##print lang, filename, line
                if len(line.split('\t')) < 2:
                    continue
                text = line.split('\t')[1]
                header = True
                header_index = int(line.split('\t')[0][2:])
                ##print header, header_index, text
            elif line.startswith("#P"):
                idx, text = line.split('\t')
                thisparaid, sentid = idx.split()
                thisparaid = int(thisparaid.split('\t')[0][2:])+1
                sentid = int(sentid.split('\t')[0][2:])+1
                #text = tokenize(text, lang)
                
                ##print text
                ##print text2naf(text, sentid, thisparaid)
                
                if lang == 'cmn':
                    lines.append(text)
                else:
                    tagged_text = pos_tag(tokenize(text,lang), lang)
                    tokens, tags = zip(*tagged_text)
                    tl, newwordid = text2naf(" ".join(tokens), sentid, 
                                             thisparaid,wordid)
                    textlayer.append(tl)
                    termlayer.append(term2naf(tokens, tags, wordid))
                    wordid = newwordid
        
        if lang == 'cmn':
            tagged_texts = pos_tag(tokenize(lines,lang, batch=True), 
                                   lang, batch=True)
            
            for tagged_text in tagged_texts:
                tokens, tags = zip(*tagged_text)
                tl, newwordid = text2naf(" ".join(tokens), sentid, 
                                         thisparaid,wordid)
                textlayer.append(tl)
                termlayer.append(term2naf(tokens, tags, wordid))
                wordid = newwordid
        
        fout.write("\n".join(textlayer) + '\n')
        fout.write("</text>"+'\n')
        fout.write("\n".join(termlayer)+'\n')
        fout.write(r'<\naf>'+'\n')
        
##print count