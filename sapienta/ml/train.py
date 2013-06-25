"""Entrypoint and utility functions for training SAPIENTA model
"""

from __future__ import division

import avl
import os
import logging
import cPickle
import crfsuite

from collections import Counter
from sapienta.ml.crf import AttributeGenerator, Trainer

class SAPIENTATrainer:


    def __init__(self):
        """Create a sapienta trainer object"""
        self.logger = logging.getLogger(__name__)

        self.accum_tp = Counter()
        self.accum_fp = Counter()
        self.accum_fn = Counter()

    def calcPrecRecall(self, trueLabels, predictedLabels, probabilities):
        labels = set(trueLabels).union(set(predictedLabels))
        tp = {}
        fp = {}
        fn = {}
        for label in labels:
            tp[label] = fp[label] = fn[label] = 0
        
        predictedZip = zip(predictedLabels, probabilities)
        self.logger.info("True label, Predicted Label, Probability")

        for true, predictedZip in zip(trueLabels, predictedZip):
            predictedLabel, probability = predictedZip
            self.logger.info("%s, %s, %s", true, predictedLabel, probability)
            if true == predictedLabel:
                tp[true] += 1
                self.accum_tp[true] += 1
            else:
                fp[predictedLabel] += 1
                fn[true] += 1

                self.accum_fp[predictedLabel] += 1
                self.accum_fn[true] += 1

        for label in labels:
            self.logger.info(label)
            if tp[label] == 0:
                prec = 0
                rec = 0
            else:
                prec = tp[label] / (tp[label] + fp[label])
                rec = tp[label] / (tp[label] + fn[label])

            self.logger.info('prec: %d tp / (%d tp + %d fp) = %f', tp[label], tp[label], fp[label], prec)
            self.logger.info('rec: %d tp / (%d tp + %d fn) = %f', tp[label], tp[label], fn[label], rec)
            self.logger.info('F-measure: %f',(2 * prec * rec) / (prec + rec))

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

            self.foldNo = f

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

            #train the mode
            self.logger.info("Starting train/test cycle for fold %d", self.foldNo)
            modelFile = self.train(allFiles, excludeList=testFiles)
            self.testModel(modelFile, testFiles)


        #now show total microaverages for models

        for label in self.accum_tp:
            self.logger.info(label)
            if tp[label] == 0:
                prec = 0
                rec = 0
            else:
                prec = self.accum_tp[label] / (self.accum_tp[label] + self.accum_fp[label])
                rec = self.accum_tp[label] / (self.accum_tp[label] + self.accum_fn[label])

            self.logger.info('prec: %d tp / (%d tp + %d fp) = %f', self.accum_tp[label], self.accum_tp[label], self.accum_fp[label], prec)
            self.logger.info('rec: %d tp / (%d tp + %d fn) = %f', self.accum_tp[label], self.accum_tp[label], self.accum_fn[label], rec)
            self.logger.info('F-measure: %f',(2 * prec * rec) / (prec + rec))



    #------------------------------------------------------------------------------------------------
    def testModel( self, modelPath, testFiles):
        
        tagger = crfsuite.Tagger()
        tagger.open(modelPath)

        allTrueLabels = []
        allPredictedLabels = []
        allProbabilities = []

        self.logger.info("Testing model from fold %d", self.foldNo)
        self.logger.info('using subset of size %d for testing', len(testFiles))

        ngramFilter = lambda l, n: n in self.ngrams[l]
        
        for doc in testFiles:
            features = self.extractFeatures(doc)
            itemSequence = crfsuite.ItemSequence()
            trueLabels = []
            
            for sentence in features:
                self.logger.debug('sentence: %s', sentence.content.encode('ascii', 'ignore'))
                label = str(sentence.corescLabel)
                trueLabels.append(label)
                
                item = crfsuite.Item()
                candcFeatures = sentence.candcFeatures
                candcFeatures.trigrams = [] # remove trigrams
                del sentence.candcFeatures
                for candcAttrib in AttributeGenerator.yieldCandcAttributes(candcFeatures, ngramFilter=ngramFilter):
                    self.logger.debug('parser feature: %s', candcAttrib.attr)
                    item.append(candcAttrib)
                for positionAttrib in AttributeGenerator.yieldPositionAttributes(sentence):
                    self.logger.debug('position feature: %s', positionAttrib.attr)
                    item.append(positionAttrib)
                itemSequence.append(item)
                
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
            
        self.calcPrecRecall(allTrueLabels, allPredictedLabels, allProbabilities)

    #------------------------------------------------------------------------------------------------

    def preprocess(self, filenames):
        """Extract initial features from the files and collect ngrams"""

        from sapienta.ml.ngrams import NgramBuilder

        ngramCacheFile = os.path.join(self.cacheDir, "ngrams_fold_%d.pickle" % self.foldNo)

        if os.path.exists(ngramCacheFile):
            self.logger.info("Loading cached ngrams from file...")
            with open(ngramCacheFile, 'rb') as f:
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


            with open(ngramCacheFile, 'wb') as f:
                cPickle.dump({"unigram" : list(unigrams), "bigram" : list(bigrams) },f)


    #------------------------------------------------------------------------------------------------

    def train(self, filenames, excludeList=[]):
        """Train a model based on a list of filenames and exclude any appearing in excludeList"""
        
        
        trainfiles = [f for f in filenames if f not in excludeList]

        self.preprocess(trainfiles)

        modelPath = os.path.join(self.corpusDir, "model_fold_%d.model" % self.foldNo)

        #now train the model
        if os.path.exists(modelPath):
            return modelPath
        else:
            return self.trainCRF(trainfiles,  self.ngrams, modelPath)
        
    #------------------------------------------------------------------------------------------------
    def trainCRF(self, files, ngrams, modelPath):
        ngramFilter = lambda l, n: n in ngrams[l]

        trainer = Trainer.PrintingTrainer()

        for file in files:
            labelSequence = crfsuite.StringList()
            itemSequence = crfsuite.ItemSequence()
            
            features = self.extractFeatures(file)

            for sentence in features:
                self.logger.debug('sentence: %s', 
                        sentence.content.encode('ascii', 'ignore'))

                label = str(sentence.corescLabel)
                labelSequence.append(label)

                item = crfsuite.Item()
                candcFeatures = sentence.candcFeatures
                candcFeatures.trigrams = []

                del sentence.candcFeatures

                for candcAttrib in AttributeGenerator.yieldCandcAttributes(candcFeatures, ngramFilter=ngramFilter):
                        self.logger.debug('parser feature: %s', candcAttrib.attr)
                        item.append(candcAttrib)

                for positionAttrib in AttributeGenerator.yieldPositionAttributes(sentence):
                        self.logger.debug('position feature: %s', positionAttrib.attr)
                        item.append(positionAttrib)
                itemSequence.append(item)         

            del features
            trainer.append(itemSequence, labelSequence, 0)
                
        self.logger.info('done generating features, training...')
            
        trainer.select('l2sgd', 'crf1d')
        trainer.set('c2', '0.1')
        trainer.train(modelPath, -1)

        del trainer

        return modelPath

    #------------------------------------------------------------------------------------------------
    
    def extractFeatures(self, file):
        """Extract features from the given file and cache them"""

        from sapienta.ml.docparser import SciXML
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
            candcClient = SoapClient()
            processedSentences = []


            for sentence in doc.yieldSentences():
                candcFeatures = candcClient.getFeatures(sentence.content)
                sentence.candcFeatures = candcFeatures
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

    logging.basicConfig(level=logging.INFO)
    

    rootlog = logging.getLogger()

    from logging import FileHandler

    rootlog.addHandler(FileHandler("crossfolds.txt"))

    main()
        
