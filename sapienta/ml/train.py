"""Entrypoint and utility functions for training SAPIENTA model
"""

import os
import logging
import cPickle


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
        
        from sapienta.ml.ngrams import NgramBuilder

        self.logger.info("Beginning feature extraction")

        ngrams = NgramBuilder()

        for file in filenames:

            if file in excludeList:
                self.logger.debug("Skipping %s - its in the exclude list", file)
                continue

            #extract features (if they're not already)
            feats = self.extractFeatures(file)

            #build lemmatized ngrams collection
            ngrams.extractLemmatizedNgrams(feats)


        unigrams, bigrams = ngrams.getChosenNgrams()
        print "unigrams retained:", len(unigrams)
        print "bigrams retained:" , len(bigrams)
        import sys
        sys.exit(0)
 

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

def main():
    """Main entrypoint for training script"""

    t = SAPIENTATrainer()
    t.train_cross_folds("/home/james/tmp/foldTable.csv", "/home/james/tmp/combined/raw")


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    main()
        
