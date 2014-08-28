# -*- coding: utf8 -*-
import os, codecs, re, math
from itertools import izip

import sys; reload(sys); sys.setdefaultencoding('utf8')

# This function reads the CC-CEDICT entries into a list.
def readCedict(dic='/home/alvas/git/NTU-MC/ntumc/toolkit/cedict_ts.u8', output=None):
  reader = [x.strip() for x in codecs.open(dic,"r","utf8") if x[0]!="#"]
  if output!= None:
    outfile = codecs.open(output,"w","utf8")
  dic = []  
  for l in reader:
    #trad = l.partition(" ")[0]
    simp = l.split(" ")[1]
    #pinyin = re.findall(r'\[([^]]*)\]',l)[0]
    #gloss = l.replace(trad, "").replace(simp,"").replace(pinyin,""). \
    #          replace("[]","").strip()[1:-1]
    if output!= None:
      print>>outfile, trad + "\t" +simp + "\t" + pinyin + "\t" + gloss
    dic.append(simp)    
  return dic  

# This function is used to find the position where the punctuations occurs in 
# a sentence; these positions are used as the delimiters for chinking.
def getPunctIndice(text, option=None):
  punctuations = ["，","、","。","！",'"','(',')','[',']','？','；','-',
                  '（','）','/','-','：', ' ','《','》','…','•']
                  #'1.','2.','3.','4.','5.','6.','7.','8.','9.']
  if option == "super":
    superspliter = ["在","的"]
    punctuations = punctuations + superspliter
  punctIndice = [i for i, x in enumerate(text) if x in punctuations]
  if punctIndice == []:
  	punctIndice = [len(text)]
  return punctIndice

# By splitting up the sentences into smaller parts (i.e. chinks), it will take
# the load off the node generation and node parsing processes
def getChinks(text):
  text = addSpace(text)
  chunkpoints = getPunctIndice(text)
  pointer = 0; chunks = []
  for i, c in enumerate(chunkpoints):
    chunks.append(text[pointer:c].strip())
    chunks.append(text[c:c+1].strip())
    pointer = c+1
    if i == len(chunkpoints) -1:
      chunks.append(text[pointer:len(text)-1].strip())
  return [i for i in chunks if i !=""]

# Sometimes Chinese sentences have English words with odd spacing
# e.g. "顺便采买些喜欢的 CD 和DVD 或 vcd。"
# This functions will sort out the spaces and output:
# "顺便采买些喜欢的 CD 和 DVD 或 vcd 。"
def addSpace(text):
  currIsAscii = None; prevIsAscii = None; newsentence = ""
  for i in text:
    try:
      i.decode('ascii')
      currIsAscii = True
    except:
      currIsAscii = False
    if prevIsAscii != currIsAscii:
      newsentence+=" "
      newsentence+=i
    else:
      newsentence+=i
    prevIsAscii = currIsAscii
    while "  " in newsentence:
      newsentence = newsentence.replace("  ", " ")
  return newsentence.strip()

# Using a dictionary, this function will return the dictionary entries that 
# corresponds to the sentence tokens.
# NOTE:
# - This function returns the input chunk as a node if it is
#   -- an ascii (i.e. an English word) or
#   -- a punctuation
def getNodes (chunk,dic):
  if dic == None:
    dic = sorted(readCedict(),key=len)
    
  chunklist = []
  try:
    chunk.decode('ascii')
    chunklist.append((0,"0-1",chunk))
  except:
    punctuations = ["，","、","。","！",'"','(',')','[',']','？','；','-',
                  '（','）','/','-','：', ' ','《','》','…','•']
    numbers = ['０','１','２','３','４','５','６','７','８','９', \
             '0','1','2','3','4','5','6','7','8','9']
    if chunk in punctuations:
      chunklist.append((0,"0-1",chunk))
    else:
      marker=0; max_chunk_len=len(chunk)
      while marker < max_chunk_len+1:
        index = 0; #longest_chunk = ""; chunk_end = 0
        while index < marker:
          token = chunk[index:marker]
          if token in dic:
            #print len(chunk), str(index)+"-"+str(marker),token
            chunklist.append((int(index),str(index)+"-"+str(marker),token))
          if token in numbers:
            #print len(chunk), str(index)+"-"+str(marker),token
            chunklist.append((int(index),str(index)+"-"+str(marker),token))
          index+=1
        marker+=1
  
  # Adds unseen tokens as individual words into the list of possible nodes.
  for j,i in enumerate(chunk):
    if i not in dic:
      chunklist.append((int(j),str(j)+"-"+str(j+1),i))
  
  chunklist = [(k,i,j) for k,i,j in chunklist if j!=""]
  
  # NOTE: This is for code optimization.
  # If there is an entry in the dictionary that corresponds to a whole chunk,
  # dump the rest of the chunk nodes.
  for i in chunklist:
    if len(i[2]) == len(chunk):
      chunklist = [i]
      break
    
  return chunklist

# This is totally a bad habit of mine to work with maps instead of messy tuples.
# Basically this method sorts the nodes (in tuple format) according the nodes'
# starting position. That is accomplished by putting nodes with the same
# starting position as under the same key. 
def chunklist2Map(chunklist):
  chunkmap = {}
  prev_k = -1 ; tempchunks = []
  for k,i,j in sorted(chunklist):
    if k > prev_k and prev_k >-1:
      chunkmap[prev_k] = tempchunks
      tempchunks = []
      tempchunks.append((i.split('-')[1],j))
    else:
      tempchunks.append((i.split('-')[1],j))
    prev_k = k
  chunkmap[prev_k] = tempchunks
  return chunkmap

############################################################################
## The brand-new recursive parser to get the best possible parse of the nodes.
##
## The criteria for this parser is to favor words with longer character.
##
## The score for the different parses are calculated based on the summation of
## the length of each segment squared i.e.:
##     sum_over_each_segment(len(char_in_words)^2)
##
## This function returns the parse with the highest score.
#############################################################################

def largestChunksParser(chunk,dic=None):
  if dic == None:
    dic = sorted(readCedict(),key=len)

  chunklist = getNodes(chunk,dic)  
  chunkmap = chunklist2Map(chunklist)
  
  def getNodesAtPos (map, position):
    for i in map:
      if i == position:
        return map[i]
  
  def add2Parses(map, pointer, parses):
    currentNodes = getNodesAtPos(map,pointer)
    # Terminating end node(s).
    if currentNodes == None:
      return parses
    # Initialize start node(s).
    newparses = []
    if pointer == 0:
      for j in currentNodes:
        newparses.append(j)
    # Iterate over parses and extends the parses by selecting the nodes
    # that corresponds to the ending position of the parse.
    for l,k in enumerate(parses):
      #prevNodeEnd = k[0]
      if int(k[0]) == int(pointer):
        for m in currentNodes:
          newparses.append((m[0], k[1] + " " + m[1]))
          #parses[l] = (m[0], k[1] + " " + m[1])    
    newparses+=parses
    return newparses
  
  def calculateParseScore(parses):
    parseWithScore = []
    for i in sorted(parses):
      score = 0
      for j in unicode.split(i," "):
        score+=math.pow(len(j.decode('utf8')),2)
      parseWithScore.append((score, i))
    return parseWithScore

  pointer = 0
  possible_parses = []
  # Activating the recursive parser.
  while pointer != len(chunk.decode('utf8')):
    possible_parses = add2Parses(chunkmap, pointer, possible_parses)
    pointer+=1
  
  # A very lazy way to trim the parse forest. What it does is it kills all the  
  # parses that doesn't matches the original input chunk.
  possible_parses = list(set([i[1] for i in possible_parses \
                   if len(i[1].replace(" ","")) == len(chunk.decode('utf8'))
                   and i[1].replace(" ","") == chunk.replace(" ","") ]))
  
  parses_with_scores = calculateParseScore(possible_parses)
  #print chunk
  bestparse = sorted(parses_with_scores)[-1]
  return bestparse[1]
  
# DEPRECATED: because sometimes it generates extra tokens...
# Select the nodes from left to right, choose the token with the longest length
# as the correct node.
def left2rightGreedyParser(chunk,dic):
  chunklist = getNodes(chunk,dic)
  chunklist_biggest = chunklist2Map(chunklist)
  
  chunklist2 = []; index = 0
  longest_len, prevend = 0.0,0.0
  for i in chunklist_biggest:
    #print i,chunklist_biggest[i]
    if int(i) < prevend:
      continue
    else:
      for j,k in chunklist_biggest[i]:
        if math.pow(float(j),2) > longest_len:
          longest_len=math.pow(float(j),2)
          try:
            chunklist2[index] = k
            prevend = int(j)
          except:
            chunklist2.append(k)
    index+=1
  #print " ".join(chunklist2)
  return chunklist2

def despace(text):
  while "  " in text:
    text = text.replace("  ", " ")
  return text.strip()

def segmenter(sentence,dic=sorted(readCedict(),key=len)):
  #print dic
  #print sentence
  chunked_sent = []
  for c in getChinks(sentence):
    chunked_sent.append(largestChunksParser(c,dic))
  return despace(" ".join(chunked_sent))

##############################################################################
# A demo for mini-segmenter using sentences from NTU-MC test suite.
def minidemo():
	textfile = "/home/alvas/git/NTU-MC/ntumc/toolkit/all.cmn"
	reader = [i.strip() for i in codecs.open(textfile,'r','utf8') if i[0] !="#"]
	cmn_dic = sorted(readCedict(),key=len)

	for line in reader:
		segmented_sentence = segmenter(line)
		print line
		print segmented_sentence 
		print "#################################################"
		if despace(line.replace(" ","")) != segmented_sentence.replace(" ",""):
		  print "ERROR:", line
		  break

def tokenize(text):
    return segmenter(text).split()

minidemo()