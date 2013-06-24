"""
Utility functions for working with ngrams within sapienta
"""
from __future__ import division
from sapienta.ml.bnc import BncFilter

import avl
import logging


from collections import Counter

class NgramBuilder:
    """This class collects the most relevant ngrams from a corpus of documents"""

    #------------------------------------------------------------------------------------------------

    def __init__(self):
        """Initialise the ngram collector"""
        self.unigrams = {}
        self.bigrams  = {}
        self.doccount = 0
        self.logger = logging.getLogger(__name__)

    #------------------------------------------------------------------------------------------------
   
    def getChosenNgrams(self):
        """Assuming we've finished adding new features, extract the best ones
        """

        for u in self.unigrams:
            self.unigrams[u]['idf'] = (self.doccount / 
                    self.unigrams[u]['doc_frequency'])

        for b in self.bigrams:
            self.bigrams[b]['idf'] = (self.doccount / 
                    self.bigrams[b]['doc_frequency'])

        unigrams = avl.new( [k for k in self.unigrams 
                if self.unigrams[k]['total_frequency'] > 3] )

        bigrams  = avl.new( [k for k in self.bigrams
            if self.getGlue(k) > 5.41e-11])

        return unigrams, bigrams
                
    
    #------------------------------------------------------------------------------------------------

    def extractLemmatizedNgrams(self, features):
        """Extract lemmatized ngram information from document and add to counter"""

        #--------------------------------------------------------------
        def combine_ngram_hash( localcount,  globalhash):
            """Support function that combines a local ngram count back into the global container"""
            for x in localcount:
                if x not in globalhash:
                    globalhash[x] = { 'total_frequency' : 0, 
                        'doc_frequency' : 0, 
                        'idf' : 0}

                globalhash[x]['total_frequency'] += localcount[x]
                globalhash[x]['doc_frequency']   += 1

        #--------------------------------------------------------------

        
        self.doccount += 1
        bnc = BncFilter()
        
        for sentence in features:
            lem = sentence.lemmatized

            unicount = Counter()
            bicount = Counter()

            unigrams = [word for word in lem.split(" ") if not bnc.isStopWord(word)]

            for word in unigrams:
                if word in unigrams:
                    unicount[word] += 1


            for i in range(len(unigrams) - 1):
                bigram = (unigrams[i] + " " + unigrams[i + 1])
                bicount[bigram] += 1

            combine_ngram_hash( unicount, self.unigrams )
            combine_ngram_hash( bicount,  self.bigrams)

        self.logger.debug("Total Documents: %d", self.doccount)
        self.logger.debug("Total Unigrams: %d", len(self.unigrams))
        self.logger.debug("Total Bigrams: %d ", len(self.bigrams))

    #------------------------------------------------------------------------------------------------
    
    def getGlue(self, ngram):
        """Generate a probability 'glue' for this ngram"""

        words = ngram.split(" ")
        order = len(words)

        totalUnis = len(self.unigrams)
        totalBis  = len(self.bigrams)

        if order == 1:
            glue = self.unigrams[ngram]['total_frequency']/ totalUnis

        elif order == 2:
            glue12 = self.bigrams[ngram]['total_frequency'] / totalBis

            glue1  = self.unigrams[words[0]]['total_frequency'] / totalUnis
            if glue1 == 0:
                glue1 = 1 / totalUnis

            glue2  = self.unigrams[words[1]]['total_frequency'] / totalUnis

            if glue2 == 0:
                glue2 = 1 / totalUnis

            glue = glue12 * glue12 / glue1 * glue2

        return glue
