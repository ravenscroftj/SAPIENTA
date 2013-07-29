"""A set of tools and utilities for producing SVMLight compatible sentence data
"""
import avl
import cPickle
from svmutil import *

from sapienta.ml.train import SAPIENTATrainer

from collections import Counter

ALL_CORESCS = ["Obj","Res","Goa","Mot","Hyp","Met","Bac","Exp","Con","Obs","Mod"]

class SVMLightTrainer(SAPIENTATrainer):
    """SAPIENTA trainer that produces SVMLight formatted training/testing data
    """


    def train(self, trainfiles):
        self.preprocess(trainfiles)

        encoder = SVMLightEncoder(self.ngrams)

        cats = sorted(ALL_CORESCS)

        labelList = []
        featList  = []
        
        f = open("features.svm", 'wb')

        for file in trainfiles:

            sents = self.extractFeatures(file)

            encoder.writeSentences(sents, f)

            self.logger.info("Encoding features from %s as SVMLight", file)
            for sent in sents:
                label = sent.corescLabel
                encoded = encoder.encodeSentence(sent)

                featList.append(encoded)
                labelList.append(cats.index(label) + 1)


            self.logger.info("Currently have %d label:sentence pairs",
            len(featList))

        #close the features file
        f.close()

        self.logger.info("Training SVM Model...")

        m = svm_train(labelList, featList, '-t 0 -b 1')

        svm_save_model(self.modelFile,m)


    def testModel( self, testFiles):
            
        self.logger.info("Loading cached ngrams from %s", self.ngramCacheFile)

        with open(self.ngramCacheFile, 'rb') as f:
                self.ngrams = cPickle.load(f)
                self.ngrams['unigram'] = avl.new(self.ngrams['unigram'])
                self.ngrams['bigram']  = avl.new(self.ngrams['bigram'])


        encoder = SVMLightEncoder(self.ngrams)

        #load the model
        m = svm_load_model(self.modelFile)

        allTrueLabels = []
        allPredictedLabels = []

        for doc in testFiles:
            sents = self.extractFeatures(doc)

            #encoder.writeSentences(sents)

            labels = []
            feats  = []

            for sent in sents:
                label = sent.corescLabel
                encoded = encoder.encodeSentence(sent)
                labels.append(label)
                feats.append(encoded)

            all_labs = sorted(ALL_CORESCS)

            #do the prediction
            num_labels = [ (all_labs.index(l)+1) for l in labels]
            p_labs, p_acc, p_vals = svm_predict(num_labels, feats, m)

            allTrueLabels += labels
            allPredictedLabels += [ labels[int(i)] for i in p_labs]

        return allTrueLabels, allPredictedLabels, [1] * len(allPredictedLabels)

#---------------------------------------------------------------------------------------

class SVMLightEncoder:
    """Given a feature list, map actual feature values to SVMLight indices"""

    def __init__(self, ngrams):

        self.ngrams = ngrams

    def encodeSentence(self, sent):
        """Given a sentence, return svmlight syntax for features within it
        """

        baseFeatureIndex = 1

        candcSentence = sent.candcFeatures
        
        sentFeatures = Counter()

        #first, we do absolute location of the sentence within the paper
        sentFeatures[baseFeatureIndex] = ord(sent.absoluteLocation) - 64
        baseFeatureIndex += 1

        #next we are concerned with the length of the sentence (A-F -> 1-6)
        sentFeatures[baseFeatureIndex] = ord(sent.length) - 64
        baseFeatureIndex += 1

        #now we insert struct-1 i.e. which third of the paper the sentence is in
        sentFeatures[baseFeatureIndex] = ord(sent.locationInHeader) - 64
        baseFeatureIndex += 1

        #now insert section/header ID
        sentFeatures[baseFeatureIndex] = sent.headerId
        baseFeatureIndex += 1

        for label, ngrams in {'unigram' : candcSentence.unigrams, 'bigram':candcSentence.bigrams }.items():

            for ngram in ngrams:
                idx = self.ngrams[label].index(ngram)
                sentFeatures[(idx + baseFeatureIndex)] = 1

            baseFeatureIndex += len(ngrams)

        return sentFeatures
    
    def writeSentences(self, sents, modfile):
        """Write a set of sentence features to an SVMLight output stream
        """
        labelList = []
        featList  = []


        cats = sorted(ALL_CORESCS)

        for sent in sents:
            label = sent.corescLabel
            encoded = self.encodeSentence(sent)

            catnum = cats.index(label) + 1

            labelList.append(catnum)
            featList.append(encoded)

        for i in range(0, len(labelList)):
            modfile.write("%d %s\n" % (labelList[i], " ".join([ "%d:%d" % (f, featList[i][f]) for f in sorted(featList[i]) ])))

