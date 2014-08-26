# -*- coding: utf-8 -*-
# Gale-Church Algorithm
# Original version from GaChalign: http://goo.gl/17t9UG
# Authors: Liling Tan

import math, functools, io, sys
from itertools import groupby, izip

import numpy as np

class LanguageIndependent():
    """
    The original Gale-Church (1993) provided the following parameters given
    the UBS trilingual corpus.
    
    Category        Freq    Prob(match)
    ==================================================
    1-1             1167     p(1-1) = 0.89
    1-0 or 0-1        13     p(1-0) = p(0-1) = 0.0099
    2-1 or 1-2       117     p(2-1) = p(1-2) = 0.089
    2-2               15     p(2-2) = 0.011
    ==================================================
                    1312     1.00
    
    Table 5: Sentence alignment types.
    
    parameters        eng-deu    eng-fre    'language independent'
    =============================================================
    c    (mean)        1.1        1.06           1.0
    s^2  (variance)    7.3        5.6            6.8
    
    c and s^2 numbers from pp. 8 of Gale-Church (1993)
    """
    def __init__(self):
        self.penalty = {(0, 1): 450,  # inserted   : -100 * log(p(0,1))/p(1,1))
                        (1, 0): 450,  # deleted    : -100 * log(p(1,0))/p(1,1))
                        (1, 1): 0,    # substituted: -100 * log(p(1,1))/p(1,1))
                        (2, 1): 230,  # contracted : -100 * log(p(2,1))/p(1,1))
                        (1, 2): 230,  # expanded   : -100 * log(p(1,1))/p(1,1))
                        (2, 2): 440   # merged     : -100 * log(p(2,2))/p(1,1))
                        }
        
        self.mean = 1
        self.variance = 6.8


LOG2 = math.log(2)

def norm_cdf(z):
    """ 
    Returns the area under a normal distribution from -inf to z standard 
    deviations. Equation 26.2.17 from Abramowitz and Stegun (1964:p.932)
    """
    t = 1.0 / (1 + 0.2316419*z) # t = 1/(1+pz) , p=0.2316419
    probdist = 1.0 - t * (0.319381530  +  
                          t * (-0.356563782 + 
                               t * (1.781477937 + 
                                    t * (-1.821255978 + 
                                         t * 1.330274429))))
    return probdist

def norm_logsf(z):
  """ Take log of the survival function for normal distribution. """
  try:
    return math.log(1 - norm_cdf(z))
  except ValueError:
    return float('-inf')

def sent_length(sentence, option='char'):
    """ Returns sentence length. """
    if option in ['char', 'character']:
        # Returns no. of chars in sentence without spaces.
        return len(sentence) - sentence.count(' ')
    elif option in ['token', 'word']:
        # Returns no. of tokens in sentences delimited by spaces.
        return sentence.count(' ') + 1

def length_cost(source_sents_lens, target_sents_lens, mean, variance):
    """  
    Calculate length cost given a list of source sentences lengths and 
    target sentences lengths. 
    
    Note: The function takes subsets of the source_sents_lens and 
    target_sents_lens from _align().
     
    The original Gale-Church (1993:pp. 81) paper considers l2/l1 = 1 hence:
        
        delta = (l2-l1*c)/math.sqrt(l1*s2)
    
    If l2/l1 != 1 then the following should be considered:
    
        delta = (l2-l1*c)/math.sqrt((l1+l2*c)/2 * s2)
    
    substituting c = 1 and c = l2/l1, gives the original cost function.
    
    :type source_sents_lens: int
    :param source_sent_len: length of a source sentence
    
    :type target_sents_lens: int
    :param target_sent_len: length of a target sentence
    
    :type mean: float
    :param mean: the mean (c) parameter in gale-church algorithm
    
    :type variance: float
    :param variance: the variance (s^2) parameter in gale-church algorithm
    """
    l1, l2 = sum(source_sents_lens), sum(target_sents_lens)
    try:
        delta = (l1 - l2 * mean) / math.sqrt( (l1 + l2 * mean) / 2 * variance)
    except ZeroDivisionError:
        return float('-inf')
    return -100 * (LOG2 + norm_logsf(abs(delta)))

def trace(tracebacks, num_source_sents, num_target_sents, 
          option='lastpair', debugging=False):
    """
    Traverse the alignment cost from the tracebacks and retrieves
    appropriate sentence pairs.
    """
    if debugging:
        for i in sorted(tracebacks.items()):
            print i
        print '#########'
        
    alignments = []

    if option == 'lastpair':
        """
        Start traversing from the last pair of sentence, the last most pair
        gets selected and point moves according to alignment type.
        same as @vchahun's implementation: http://goo.gl/cr9YHz
        
        Traversing is similar to NLTK's implementation: http://goo.gl/XIjJhE
        but note that NLTk saves the tracebacks differently. 
        """
        i,j =  num_source_sents, num_target_sents
        prev_i, prev_j = i, j 
        while True:
            (c, di, dj) = tracebacks[i,j] # (di, dj) is the alignment type.
            if di == dj == 0:
                break
            alignments.append(((i-di, i), (j-dj, j)))
            i -= di; j -= dj
    '''
    # TODO: more traversing methods.
    # Traverse from the end, retrieves the minimal cost using beam search.
    elif option == 'beam':
        prev_i, prev_j = num_source_sents + 1, num_target_sents + 1
        for i in reversed(range(num_source_sents + 1)):
            traces = [tracebacks[i,j]+(j,) for j in range(num_target_sents + 1)]
            # Selects possible path with min cost.
            for t in sorted(traces):
                cost, di, dj,j = t
                if di == dj == 0:
                    break
                if i-di >=0 and j-dj >=0 and \
                i-di < prev_i and j-dj < prev_j: # Checks for possible path.
                    alignments.append(((i-di, i), (j-dj, j)))
                    break
                    i -= di
                    prev_i = i
                    prev_j = j
    '''
    return reversed(alignments)        
    
def _align(source_sents_lens, target_sents_lens, mean, variance, penalty):
    """ 
    The minimization function to choose the sentence pair with 
    cheapest alignment cost.
    
    :type source_sents_lens: list
    :param source_sents_lens: list of source sentences' lengths
    
    :type target_sents_lens: list
    :param target_sents_lens: list of target sentences' lengths
    
    :rtype: alignments_blocks: list
    :return: list of tuple of tuple sentence indices, e.g.
        
        [ ((0,1), (0,2)), ((1,4), (2,3)) ]
    
    i.e. the first source sentence aligns with the first two target sentences
    and the 2nd to 4th source sentence aligns to the third target sentence.
    """
    # Stores the tracebacks for alignment costs between sentence pairs.
    tracebacks = {}
    for i in range(len(source_sents_lens) + 1):
        for j in range(len(target_sents_lens) + 1):
            if i == j == 0:
                tracebacks[0,0] = (0, 0, 0)
            else:
                tracebacks[i,j] = min((tracebacks[i-di, j-dj][0] + 
                                       length_cost(source_sents_lens[i-di:i],
                                                  target_sents_lens[j-dj:j],
                                                  mean, variance) + 
                                       pen_cost, di, dj)
                                      for (di,dj), pen_cost in penalty.items()
                                      if i-di>=0 and j-dj>=0)
                '''
                # More humanly, read this:
                min_cost = (float('inf'), 0, 0)
                # For each sentence pair, minimize the cost of alignment
                # among the different alignment types.
                for (di,dj), pen_cost in penalty.items():
                    if i-di>=0 and j-dj>=0:
                        # Retrieves previous cost.
                        prev_cost = tracebacks[i-di, j-dj][0]
                        # Calculate length_cost.
                        len_cost = length_cost(source_sents_lens[i-di:i],
                                               target_sents_lens[j-dj:j],
                                               mean, variance)
                        # Sum previous cost, length cost and alignment penalty.
                        total_cost = prev_cost + len_cost + pen_cost
                        if total_cost < min_cost:
                            # Saves the alignment type with the minimum cost.
                            tracebacks[i,j] = (total_cost, di, dj)
                ''' 
    # Retraces the alignments.
    num_source_sents = len(source_sents_lens)
    num_target_sents = len(target_sents_lens)
    return trace(tracebacks, num_source_sents, num_target_sents)

def align(source_sents, target_sents, mean, variance, penalty, option='char'):
    """
    Main alignment function.

    :type source_sents: list
    :param source_sents: list of source sentences
    
    :type target_sents: list
    :param target_sents: list of target sentences
    
    :type mean: float
    :param mean: the mean (c) parameter in gale-church algorithm
    
    :type variance: float
    :param variance: the variance (s^2) parameter in gale-church algorithm
    
    :type penalty: dict
    :param penalty: a dictionary of the cost penalty parameter in 
    gale-church algorithm, the (key,value) pairs stores the alignment types and
    their respective penalty costs
    """
    # Collects the source and target sentence lengths.
    source_sents_lens = map(functools.partial(sent_length, option=option), 
                            source_sents)
    target_sents_lens = map(functools.partial(sent_length, option=option), 
                            target_sents)
    
    ##print source_sents_lens, target_sents_lens
    ##print sum(source_sents_lens), sum(target_sents_lens)
    
    # Determines alignment blocks by minimizing cost function of different
    # alignment types.
    for (i_start, i_end), (j_start, j_end) in \
    _align(source_sents_lens, target_sents_lens, mean, variance, penalty):
        ##print (i_start, i_end), (j_start, j_end)
        source = "~~".join(source_sents[i_start:i_end])
        target = "~~".join(target_sents[j_start:j_end])
        yield "\t".join([source, target]) 

##########################################################################
# GaChalign specify code.
##########################################################################

def per_section(it, is_delimiter=lambda x: x.isspace()):
    ret = []
    for line in it:
        if is_delimiter(line):
            if ret:
                yield ret  # OR  ''.join(ret)
                ret = []
        else:
            ret.append(line.rstrip())  # OR  ret.append(line)
    if ret:
        yield ret
        
def per_paragraph(infile, delimiter="#"):
    return per_section(infile, lambda line: line.startswith(delimiter))
           
def text_len(text, option='char'):
    """ Calculates the length of a text without spaces. """
    if option in ['char', 'character']:
        return len(text) - text.count(' ')
    elif option in ['token', 'word']:
        return text.count(' ')+1
    
def file_len(filename, option='char'):
    """ Calculates length of file. """
    return sum(text_len(i, option=option) for i in io.open(filename))
    
def calculate_gacha_mean(srcfile, trgfile, option='char'):
    """
    Calculates mean ratio of sentence length between source and target language,
    i.e. 
        sum(#chars in source sents)  / sum(#chars in target sents)
    
    :type srcfile: str
    :param srcfile: filename of the file containing the source language texts.
    
    :type trgfile: str
    :param trgfile: filename of the file containing the target language texts.
    """
    return file_len(srcfile, option=option)/float(file_len(trgfile, option=option))

def calculate_gacha_variance(srcfile, trgfile, option='char'):
    """
    Calculates variance of text, i.e.
    derivative of the sum of squares of paragraphs' length differences against 
    the sum of #chars in source paragraphs
    """
    paragraph_len_diffs = []
    source_paragraph_lens = []
    with io.open(srcfile) as src, io.open(trgfile) as trg:
        src = per_paragraph(src, '#')
        trg = per_paragraph(trg, '#')
        for s,t in izip(src, trg):
            srclen = text_len(s, option=option)
            trglen = text_len(t, option=option)
            paragraph_len_diffs.append(math.pow((srclen - trglen),2))
            source_paragraph_lens.append(srclen)
    m, __ = np.polyfit(source_paragraph_lens, paragraph_len_diffs, 1)
    return m

##########################################################################
# File reading and command-line usage
##########################################################################

parameters = LanguageIndependent()

def main(source_corpus, target_corpus, mean=parameters.mean, 
         variance=parameters.variance, penalty= parameters.penalty, 
         option='char', delimiter='#'):
    if mean == 'gacha': # Automatically recalculate mean and variance parameter.
        option = 'char'
        mean = calculate_gacha_mean(source_corpus, target_corpus, option=option)
        variance = calculate_gacha_variance(source_corpus, target_corpus,
                                            option=option)
    # Show Users the mean/variance.
    msg = " ".join(["Aligning corpus with mean =", str(mean), 
                    "and variance = ", str(variance), '\n'])
    sys.stderr.write(msg)
    
    with io.open(source_corpus) as src, io.open(target_corpus) as trg:
        src = per_paragraph(src, delimiter=delimiter)
        trg = per_paragraph(trg, delimiter=delimiter)
        for s,t in izip(src, trg):
            for sentence_pair in align(s,t, mean, variance, penalty):
                print sentence_pair
                
def gachalign(source_corpus, target_corpus, mean=parameters.mean, 
         variance=parameters.variance, penalty= parameters.penalty, 
         option='char', delimiter='#'):
    main(source_corpus, target_corpus, mean, variance, penalty, option, delimiter)
            
if __name__ == '__main__':
  if len(sys.argv) not in range(3,6):
    sys.stderr.write('Usage: python %s corpus.x corpus.y '
                     '(option) (mean) (variance)\n' % sys.argv[0])
    sys.exit(1)
  main(*sys.argv[1:])
    