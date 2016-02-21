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

        encoder = SVMLightEncoder(self.ngrams, self.logger)

        cats = sorted(ALL_CORESCS)

        labelList = []
        featList  = []
        

        for file in trainfiles:

            sents = self.extractFeatures(file)

            self.logger.info("Encoding features from %s as SVMLight", file)
            for sent in sents:
                label = sent.corescLabel
                encoded = encoder.encodeSentence(sent)


                try:
                    lindex = cats.index(label) + 1


                    featList.append(encoded)

                    labelList.append(lindex)
                except:
                    self.logger.warn("Skipping sentence with no valid label: SENT: '%s', LABEL: '%s' ", sent, label)
                    continue

            self.logger.info("Currently have %d label:sentence pairs",
            len(featList))


        self.logger.info("Training SVM Model...")

        m = svm_train(labelList, featList, '-t 0 -b 1')

        svm_save_model(self.modelFile,m)


    def testModel( self, testFiles):
            
        self.logger.info("Loading cached ngrams from %s", self.ngramCacheFile)

        with open(self.ngramCacheFile, 'rb') as f:
                self.ngrams = cPickle.load(f)
                self.ngrams['unigram'] = avl.new(self.ngrams['unigram'])
                self.ngrams['bigram']  = avl.new(self.ngrams['bigram'])


        encoder = SVMLightEncoder(self.ngrams, self.logger)

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

                if label in ALL_CORESCS:

                    labels.append(label)
                    feats.append(encoded)

                else:
                    self.logger.warn("Skipping sent '%s' because invalid label '%s'", sent,label)

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

    def __init__(self, ngrams, logger):

        self.ngrams = ngrams
        self.logger = logger

    def encodeSentence(self, sent):
        """Given a sentence, return svmlight syntax for features within it
        """

        baseFeatureIndex = 1

        candcSentence = sent.candcFeatures
        
        sentFeatures = {}

        #first, we do absolute location of the sentence within the paper
        sentFeatures['absloc'] = ord(sent.absoluteLocation) - 64

        #next we are concerned with the length of the sentence (A-F -> 1-6)
        sentFeatures['sentlen'] = ord(sent.length) - 64

        #now we insert struct-1 i.e. which third of the paper the sentence is in
        sentFeatures['struct-1'] = sent.locationInHeader

        #now insert section/header ID
        sentFeatures['section_id'] = sent.headerId

        for label, ngrams in {'unigram' : candcSentence.unigrams, 'bigram':candcSentence.bigrams }.items():

            for ngram in ngrams:
                idx = self.ngrams[label].index(ngram)
                sentFeatures[ngram] = 1


        for verb in candcSentence.verbs:
            sentFeatures['verb_%s' % verb] = 1

        for verbclass in candcSentence.verbClasses:
            sentFeatures['verbClass_%s' % verbclass] = 1

        for verbpos in candcSentence.verbsPos:
            sentFeatures['verbPos_%s' % verbpos] = 1

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

            try:
                catnum = cats.index(label) + 1
            except:
                self.logger.warn("Skipping sentence with no valid label: SENT: '%s', LABEL: '%s' ", sent, label)
                continue

            labelList.append(catnum)
            featList.append(encoded)

        for i in range(0, len(labelList)):
            modfile.write("%d %s\n" % (labelList[i], " ".join([ "%d:%d" % (f, featList[i][f]) for f in sorted(featList[i]) ])))

