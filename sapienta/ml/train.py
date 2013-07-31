"""Entrypoint and utility functions for training SAPIENTA model
"""

from __future__ import division

import avl
import os
import logging
import cPickle
import crfsuite

from sapienta.ml.crf import AttributeGenerator, Trainer

class DummyLock:
    def __enter__(self):
        pass
    def __exit__(self,exc_type, exc_value, traceback):
        pass

class FeatureExtractorBase:
    """This class has some reusable functions for extracting features
    """

    def __init__(self, modelFile, ngramsFile, cacheDir, features, logger=None,
    lock=None):
        self.modelFile = modelFile
        self.ngramCacheFile = ngramsFile
        self.cacheDir = cacheDir
        self.features = features

        if logger == None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger


        #lock used for multithreaded training only
        #if we're not multithreaded we use a "dummy" lock

        if lock != None:
            self.lock  = lock
        else:
            self.lock = DummyLock()

    #------------------------------------------------------------------------------------------------
    
    def extractFeatures(self, file, cache=True):
        """Extract features from the given file and cache them"""

        from sapienta.ml.docparser import SciXML
        from sapienta.ml.candc import SoapClient

        cachedName = os.path.join(self.cacheDir, os.path.basename(file))

        if os.path.exists(cachedName):

            self.logger.info("Loading features from %s", cachedName)
            with self.lock:
                with open(cachedName, 'rb') as f:
                    features = cPickle.load(f)
                return features

        else:
            self.logger.info("Generating features for %s", file)

            parser = SciXML()
            doc = parser.parse(file)
            candcClient = SoapClient()
            processedSentences = []


            for sentence in doc.yieldSentences():
                candcFeatures = candcClient.getFeatures(sentence.content)
                sentence.candcFeatures = candcFeatures
                processedSentences.append(sentence)
        
            if cache:
                self.logger.debug("Caching features at %s", cachedName)

                with self.lock:
                    with open(cachedName, 'wb') as f:
                        cPickle.dump(processedSentences, f, -1)

            return processedSentences

    #------------------------------------------------------------------------------------------------
    def crfdataForFeatures(self, features):
        """Get a list of labels and crf 'features' from a list of features
        """
        labelSequence = crfsuite.StringList()
        itemSequence = crfsuite.ItemSequence()
        ngramFilter = lambda l, n: n in self.ngrams[l]

        for sentence in features:
            self.logger.debug('sentence: %s', 
                    sentence.content.encode('ascii', 'ignore'))

            label = str(sentence.corescLabel)
            labelSequence.append(label)

            item = crfsuite.Item()
            candcFeatures = sentence.candcFeatures
            candcFeatures.trigrams = []

            del sentence.candcFeatures

            for candcAttrib in AttributeGenerator.yieldCandcAttributes(self.features, candcFeatures, 
                                                                ngramFilter=ngramFilter):

                    self.logger.debug('parser feature: %s', candcAttrib.attr)
                    item.append(candcAttrib)

            for positionAttrib in AttributeGenerator.yieldPositionAttributes(self.features, sentence):
                    self.logger.debug('position feature: %s', positionAttrib.attr)
                    item.append(positionAttrib)
            itemSequence.append(item)  

        return itemSequence, labelSequence


#-----------------------------------------------------------------------------

class SAPIENTATrainer(FeatureExtractorBase):
    """Base class for training systems and preprocessing features"""
    def __init__(self, features, cacheDir, modelFile, ngramCacheFile, logger=None, lock=None):
        """Create a sapienta trainer object"""

        FeatureExtractorBase.__init__(self, modelFile, ngramCacheFile,
        cacheDir, features, logger, lock)


    #------------------------------------------------------------------------------------------------

    def preprocess(self, filenames):
        """Extract initial features from the files and collect ngrams"""

        from sapienta.ml.ngrams import NgramBuilder

        if os.path.exists(self.ngramCacheFile):
            self.logger.info("Loading cached ngrams from file...")
            with open(self.ngramCacheFile, 'rb') as f:
                self.ngrams = cPickle.load(f)
                self.ngrams['unigram'] = avl.new(self.ngrams['unigram'])
                self.ngrams['bigram']  = avl.new(self.ngrams['bigram'])
        else:

            self.logger.info("Beginning feature extraction")

            ngrams = NgramBuilder()

            

            for file in filenames:

                #extract features (if they're not already)
                feats = self.extractFeatures(file)

                #build lemmatized ngrams collection
                ngrams.extractLemmatizedNgrams(feats)

            #retain sets of unigrams and bigrams
            unigrams, bigrams = ngrams.getChosenNgrams()
            self.logger.info("Unigrams retained: %d",len(unigrams))
            self.logger.info("BiGrams retained: %d", len(bigrams))

            self.ngrams = { "unigram" : unigrams, "bigram" : bigrams  }


            with open(self.ngramCacheFile, 'wb') as f:
                cPickle.dump({"unigram" : list(unigrams), "bigram" : list(bigrams) },f)


    #------------------------------------------------------------------------------------------------

    def train(self, trainfiles):
        """Stub overriden by concrete implementations to do preprocessing and training
        """
        raise Exception("Not implemented! Use a subclass of SAPIENTATrainer")

    #------------------------------------------------------------------------------------------------
    
    def extractFeatures(self, file):
        """Extract features from the given file and cache them"""

        from sapienta.ml.docparser import SciXML
        from sapienta.ml.candc import SoapClient


        cachedName = os.path.join(self.cacheDir, os.path.basename(file))

        if os.path.exists(cachedName):

            self.logger.info("Loading features from %s", cachedName)
            with self.lock:
                with open(cachedName, 'rb') as f:
                    features = cPickle.load(f)
                return features

        else:
            self.logger.info("Generating features for %s", file)

            parser = SciXML()
            doc = parser.parse(file)
            candcClient = SoapClient()
            processedSentences = []


            for sentence in doc.yieldSentences():
                candcFeatures = candcClient.getFeatures(sentence.content)
                sentence.candcFeatures = candcFeatures
                processedSentences.append(sentence)
        
            self.logger.debug("Caching features at %s", cachedName)

            with self.lock:
                with open(cachedName, 'wb') as f:
                    cPickle.dump(processedSentences, f, -1)

            return processedSentences


#--------------------------------------------------------------------------------------------------


class CRFTrainer(SAPIENTATrainer):
    """Specific implementation of SAPIENTA trainer that uses CRFSuite for training"""

    def train(self, trainfiles):
        self.preprocess(trainfiles)
        self.trainCRF(trainfiles)

    #------------------------------------------------------------------------------------------------
    def trainCRF(self, files):
        """Train the CRFSuite system using features extracted from files
        """

        trainer = Trainer.LoggingTrainer(self.logger)

        for file in files:
            labelSequence = crfsuite.StringList()
            itemSequence = crfsuite.ItemSequence()
            features = self.extractFeatures(file)
            itemSequence, labelSequence = self.crfdataForFeatures(features)
            trainer.append(itemSequence, labelSequence, 0)
                
        self.logger.info('done generating features, training...')
            
        trainer.select('l2sgd', 'crf1d')
        trainer.set('c2', '0.1')
        trainer.train(self.modelFile, -1)


    #------------------------------------------------------------------------------------------------
    def testModel( self, testFiles):
        """Test a generated model using a list of testfiles and set of ngrams"""
        self.logger.info('using subset of size %d for testing', len(testFiles))

        tagger = crfsuite.Tagger()
        tagger.open(self.modelFile)

        allTrueLabels = []
        allPredictedLabels = []
        allProbabilities = []

        self.logger.info("Loading cached ngrams from %s", self.ngramCacheFile)

        with open(self.ngramCacheFile, 'rb') as f:
                self.ngrams = cPickle.load(f)
                self.ngrams['unigram'] = avl.new(self.ngrams['unigram'])
                self.ngrams['bigram']  = avl.new(self.ngrams['bigram'])

        self.logger.info("Ngram filter has %d bigrams and %d unigrams", 
                len(self.ngrams['bigram']), len(self.ngrams['unigram']))

        ngramFilter = lambda l, n: n in ngrams[l]
        
        for doc in testFiles:
            features = self.extractFeatures(doc)

            itemSequence, labelSequence = self.crfdataForFeatures(features)
            trueLabels = labelSequence

            tagger.set(itemSequence)
            predictedLabels = tagger.viterbi()
            probabilities = []
            for i, label in enumerate(predictedLabels):
                probability = tagger.marginal(label, i)
                probabilities.append(probability)

            #done with this file, add results to global list                
            allTrueLabels += trueLabels
            allPredictedLabels += predictedLabels
            allProbabilities += probabilities

        return allTrueLabels, allPredictedLabels, allProbabilities
            
def main():
    """Main entrypoint for training script"""
    from argparse import ArgumentParser

    a = ArgumentParser(description='Train an annotation model with a list of papers')

    a.add_argument('--features', dest='features', action='store', default=None,
            help="List of features used in training separated by commas.")


    a.add_argument('paperDirectory', metavar='paper_dir',
        help='Location of XML papers to train the model on')

    a.add_argument('modelFile', metavar='model_file',
        help='The file in which the model should be stored.')

    args = a.parse_args()

    features = ['ngrams', 'verbs', 'verbclass','verbpos', 'passive','triples','relations','positions' ]

    cacheDir = os.path.join(args.paperDirectory, "cachedFeatures")

    ngramsFile = os.path.join(args.paperDirectory, "ngrams.pickle")
    
    trainer = SAPIENTATrainer(features, cacheDir, args.modelFile, 
        ngramsFile, logging.getLogger("sapienta.trainer"))
    
    all_papers = [ os.path.join(args.paperDirectory,f) for f in
    os.listdir(args.paperDirectory) if f.endswith(".xml")]
    
    trainer.train(all_papers)


#allows other modules to import a 'default' trainer that we select
DefaultTrainer = CRFTrainer
if __name__ == "__main__":
    
    logging.basicConfig(level=logging.INFO)
    
    rootlog = logging.getLogger()


    main()
