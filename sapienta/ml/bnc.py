'''
Created on 8 Mar 2012

read BNC word frequency provided by http://www.kilgarriff.co.uk/bnc-readme.html

@author: grabmuel
'''
import os


class BncFilter:
    
    maxlines = 100
    bncFreqPath = os.environ['SAPIENTA_STOPWORDS_LIST'] 
    def __init__(self):
        self.stopwords = set()
        f = open(BncFilter.bncFreqPath)
        f.readline() #skip header
        for i, line in enumerate(f):
            word = line.split(' ')[1]
            self.stopwords.add(word)
            if i == BncFilter.maxlines:
                break
            
    def isStopWord(self, token):
        return token in self.stopwords
