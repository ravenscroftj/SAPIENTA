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
        self.trigrams = {}
        self.antecedents = {}
        self.successors = {}
        self.doccount = 0
        self.logger = logging.getLogger(__name__)
        self.totalUnis = self.totalBis = self.totalTris = 0

    #------------------------------------------------------------------------------------------------
   
    def getChosenNgrams(self):
        """Assuming we've finished adding new features, extract the best ones
        """

        self.logger.info("Collecting antecedents and successors for ngrams")
        #grab all antecedents and successors for bigrams
        map( self.collect_antecedents, self.bigrams.keys())
        map( self.collect_antecedents, self.trigrams.keys())

        self.logger.info("Running local maximum algorithm for ngrams")
        #run local maximums to get extraction information
        for lst in [self.unigrams, self.bigrams]:
            map(self.local_max_aber, lst.keys())


        self.logger.info("Extracting useful ngrams")
        for u in self.unigrams:
            self.unigrams[u]['idf'] = (self.doccount / 
                    self.unigrams[u]['doc_frequency'])

        for b in self.bigrams:
            self.bigrams[b]['idf'] = (self.doccount / 
                    self.bigrams[b]['doc_frequency'])

        unigrams = avl.new( [k for k in self.unigrams 
                if self.unigrams[k]['total_frequency'] > 3] )

        bigrams  = avl.new( [k for k in self.bigrams
            if (self.bigrams[k]['res'] and (self.getGlue(k) > 5.6e-11))])

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

        #filter out numbers and parenthesis in these ngrams
        
        for sentence in features:
            unicount = Counter(sentence.candcFeatures.unigrams)
            bicount = Counter(sentence.candcFeatures.bigrams)
            tricount = Counter(sentence.candcFeatures.trigrams)

            combine_ngram_hash( unicount, self.unigrams )
            combine_ngram_hash( bicount,  self.bigrams)
            combine_ngram_hash( tricount, self.trigrams)

            self.totalUnis += sum( [unicount[u] for u in unicount] )
            self.totalBis  += sum( [bicount[b]  for b in bicount]  )
            self.totalTris += sum( [tricount[t] for t in tricount] )

        self.logger.debug("Total Documents: %d", self.doccount)

        self.logger.debug("Total Unigrams: %d", self.totalUnis)
        self.logger.debug("Total Bigrams: %d ", self.totalBis)
        self.logger.debug("Total Trigrams: %d", self.totalTris)

    #------------------------------------------------------------------------------------------------
    
    def collect_antecedents(self, ngram):
        words = ngram.split(" ")
        order = len(words)

        if order == 1:
            self.antecedents[ngram] = []
        elif order == 2:

           if self.antecedents.has_key(ngram):
                self.antecedents[ngram] |= words
           else:
                self.antecedents[ngram] = set(words)

           for w in words:           
                if self.successors.has_key(w):
                    self.successors[w].add(ngram)
                else:
                    self.successors[w] = set([ngram])

        elif order == 3:
            nngram = [ " ".join((words[0],words[1])), " ".join((words[1],words[2]))]

            if self.antecedents.has_key(ngram):
                self.antecedents[ngram] |= nngram
            else:
                self.antecedents[ngram] = set(nngram)

            for w in nngram:
                if self.successors.has_key(w):
                    self.successors[w].add(ngram)
                else:
                    self.successors[w] = set([ngram])

    #------------------------------------------------------------------------------------------------

    def getGlue(self, ngram):
        """Generate a probability 'glue' for this ngram"""

        words = ngram.split(" ")
        order = len(words)


        if order == 1:
            glue = self.unigrams[ngram]['total_frequency'] / self.totalUnis

        elif order == 2:
            glue12 = self.bigrams[ngram]['total_frequency'] / self.totalBis

            glue1  = self.unigrams[words[0]]['total_frequency'] / self.totalUnis
            if glue1 == 0:
                glue1 = 1 / totalUnis

            glue2  = self.unigrams[words[1]]['total_frequency'] / self.totalUnis

            if glue2 == 0:
                glue2 = 1 / totalUnis

            glue = glue12 * glue12 / glue1 * glue2


        elif order == 3:
            glue123 = self.trigrams[ngram]['total_frequency'] / self.totalTris
            bi01 = " ".join(words[:2])
            bi02 = " ".join(words[1:])


            print ngram
            b1 = self.bigrams[bi01]
            u1 = self.unigrams[words[2]]

            glue01 = (self.bigrams[bi01]['total_frequency'] * 
                        self.unigrams[words[2]]['total_frequency'] 
                        / self.totalBis * self.totalUnis)

            glue12 = (self.bigrams[bi02]['total_frequency'] * 
                        self.unigrams[words[0]]['total_frequency'] 
                        / self.totalBis * self.totalUnis)

            avgglue = 1 / 2 * (glue01 + glue12)

            if avgglue == 0:
                avgglue = 1 / self.totalBis

            glue = glue123 * glue123 / avgglue


        return glue



    #------------------------------------------------------------------------------------------------
    
    def local_max_aber(self, ngram):
        """Algorithm for finding the relevance of an ngram an ML model
        """

        antsum = 0
        sucsum = 0

        words = ngram.split(" ")
        order = len(words)


        if order == 1:
            ngrams = self.unigrams
            totalNgrams = self.totalUnis
        elif order == 2:
            ngrams = self.bigrams
            totalNgrams = self.totalBis

            succsum = 0
            
            if self.successors.has_key(ngram):
                for s in self.successors[ngram]:
                    thisglue = self.getGlue(s)
                    self.logger.debug("glue of successor %s is %e", s, thisglue)
                    succsum += thisglue
            

            glue = self.getGlue(ngram)
            self.logger.debug("glue of %s is %e", ngram, glue)

            if self.successors.has_key(ngram) and (len(self.successors[ngram]) > 0):
                    glueS = glue * len(self.successors[ngram])
            else:
                glueS = glue


            ngrams[ngram]['glue'] = glue
            ngrams[ngram]['res'] = glueS > succsum

        
        #calculate tfidf for all ngrams regardless of order

        tf = ngrams[ngram]['total_frequency'] / len(ngrams)
        
        idf = self.doccount / totalNgrams

        ngrams[ngram]['tfidf'] = tf * idf

