"""Entrypoint and utility functions for training SAPIENTA model
"""

import os
import logging
import cPickle
import avl

from collections import Counter

class SAPIENTATrainer:

    def __init__(self):
        """Create a sapienta trainer object"""
        self.logger = logging.getLogger(__name__)

    #------------------------------------------------------------------------------------------------

    def train_cross_folds( self, foldsFile, corpusDir):
        """Train SAPIENTA on folds described in foldsFile."""

        from sapienta.ml.folds import get_folds
        
        self.folds = get_folds( foldsFile )
        self.corpusDir = corpusDir
        self.cacheDir = os.path.join(self.corpusDir, "cachedFeatures")

        if not os.path.exists(self.cacheDir):
            os.mkdir(self.cacheDir)
            self.logger.info("Generating feature cache directory")

        genFileName = lambda x: os.path.join(corpusDir, x['filename'] + 
                                    "_mode2." + x['annotator'] + ".xml")


        allFiles =  [f for f in [ genFileName(fdict) 
                        for x in self.folds for fdict in x ] 
                                    if os.path.exists(f)]
    

        for f, fold in enumerate(self.folds):

            testFiles = []
            sents = 0
            
            for filedict in fold:
                fname = os.path.join(corpusDir, filedict['filename'] + "_mode2." + filedict['annotator'] + ".xml")

                sents += int(filedict['total_sentence'])

                if not os.path.isfile(fname):
                    self.logger.warn("No file %s detected.", fname)
                else:
                    testFiles.append(fname)

            self.logger.info("Fold %d has %d files and %d sentences total" + 
                    " (which will be excluded)", f, len(testFiles), sents)

            #train the model
            self.train(allFiles, excludeList=testFiles)


    #------------------------------------------------------------------------------------------------

    def train(self, filenames, excludeList=[]):
        """Train a model based on a list of filenames and exclude any appearing in excludeList"""
        
        self.unigrams = {}
        self.bigrams = {}

        self.logger.info("Beginning feature extraction")

        for file in filenames:

            if file in excludeList:
                self.logger.debug("Skipping %s - its in the exclude list", file)
                continue

            #extract features (if they're not already)
            feats = self.extractFeatures(file)

            #build lemmatized ngrams collection
            self.extractLemmatizedNgrams(feats)

            self.logger.debug("Total Unigrams: %d", len(self.unigrams))
            self.logger.debug("Total Bigrams: %d ", len(self.bigrams))

        #select most relevant ngrams
        D = len([f for f in filenames if f not in excludeList])

        for u in self.unigrams:
            self.unigrams[u]['idf'] = float(D) / float( self.unigrams[u]['doc_frequency'])

        for b in self.bigrams:
            self.bigrams[b]['idf'] = float(D) / float( self.bigrams[b]['doc_frequency'])


        self.unitree = avl.new([k for k in self.unigrams if self.unigrams[k] > 3])
        self.bitree = avl.new([ k for k in self.bigrams if self.bigrams[k] > 3])

        self.logger.info("Finished unigram extraction, kept %d unigrams", len(self.unitree))
        self.logger.info("Finished bigram extraction, kept %d bigrams", len(self.bitree))
 

    #------------------------------------------------------------------------------------------------
    
    def extractFeatures(self, file):
        """Extract features from the given file and cache them"""

        from sapienta.ml.docparser import SciXML
        from sapienta.ml.lemma import Lemmatizer
        from sapienta.ml.candc import SoapClient


        cachedName = os.path.join(self.cacheDir, os.path.basename(file))

        if os.path.exists(cachedName):

            self.logger.info("Loading features from %s", cachedName)

            with open(cachedName, 'rb') as f:
                features = cPickle.load(f)
            return features

        else:
            self.logger.debug("Generating features for %s", file)

            parser = SciXML()
            doc = parser.parse(file)
            lemmatizer = Lemmatizer()
            candcClient = SoapClient()
            processedSentences = []


            for sentence in doc.yieldSentences():
                candcFeatures = candcClient.getFeatures(sentence.content)
                sentence.candcFeatures = candcFeatures
                sentence.lemmatized = lemmatizer.lemmatize_sentence(sentence.content)
                processedSentences.append(sentence)
        
            self.logger.debug("Caching features at %s", cachedName)
            with open(cachedName, 'wb') as f:
                cPickle.dump(processedSentences, f, -1)

            return processedSentences

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

        from sapienta.ml.bnc import BncFilter
        
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



           


#------------------------------------------------------------------------------------------------

def main():
    """Main entrypoint for training script"""

    t = SAPIENTATrainer()
    t.train_cross_folds("/home/james/tmp/foldTable.csv", "/home/james/tmp/combined/raw")


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    main()
        
