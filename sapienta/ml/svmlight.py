"""A set of tools and utilities for producing SVMLight compatible sentence data
"""
import avl
import cPickle
from svmutil import *

from sapienta.ml.train import SAPIENTATrainer

from collections import Counter

class SVMLightTrainer(SAPIENTATrainer):
    """SAPIENTA trainer that produces SVMLight formatted training/testing data
    """


    def train(self, trainfiles):
        self.preprocess(trainfiles)

        encoder = SVMLightEncoder(self.ngrams)

        all_sents = {}

        for file in trainfiles:
            sents = self.extractFeatures(file)
            self.logger.info("Encoding features from %s as SVMLight", file)
            for sent in sents:
                label = sent.corescLabel
                encoded = encoder.encodeSentence(sent.candcFeatures)

                encoded = { x:1 for x in encoded}

                if not label in all_sents:
                    all_sents[label] = []

                all_sents[label].append(encoded)

            self.logger.info("Currently have %d sentences in %d classes", sum(map(len,all_sents.values())), len(all_sents))


        self.logger.info("Training SVM Model...")

        cats = sorted(all_sents.keys())

        labelList = []
        featList  = []

        for label, sentences in all_sents.items():
            catnum = cats.index(label) + 1
            
            for sent in sentences:
                labelList.append(catnum)
                featList.append(sent)
        
        m = svm_train(labelList, featList, '-h 0 -c 5')

        svm_save_model(self.modelFile,m)

        #with open("features.svm", 'wb') as modfile:
        #    for i in range(0, len(labelList)):
        #        modfile.write("%d %s\n" % (labelList[i], " ".join([ "%d:%d" % (f, featList[i][f]) for f in featList[i] ])))

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

            labels = []
            feats  = []

            for sent in sents:
                label = sent.corescLabel
                encoded = encoder.encodeSentence(sent.candcFeatures)

                labels.append(label)
                feats.append(encoded)

            all_labs = sorted(list(set(labels)))

            #do the prediction
            num_labels = [ (all_labs.index(l)+1) for l in labels]
            print labels 
            p_labs, p_acc, p_vals = svm_predict(num_labels, feats, m)



            allTrueLabels += labels
            allPredictedLabels += [ labels[int(round(i))] for i in p_labs]

        return allTrueLabels, allPredictedLabels, [1] * len(allPredictedLabels)



            
#---------------------------------------------------------------------------------------

class SVMLightEncoder:

    def __init__(self, ngrams):

        self.ngrams = ngrams

    def encodeSentence(self, candcSentence):
        """Given a sentence, return svmlight syntax for features within it
        """

        baseFeatureIndex = 1
        
        sentFeatures = Counter()

        for label, ngrams in {'unigram' : candcSentence.unigrams, 'bigram':candcSentence.bigrams }.items():

            for ngram in ngrams:
                idx = self.ngrams[label].index(ngram)
                sentFeatures[(idx + baseFeatureIndex)] += 1

            baseFeatureIndex += len(ngrams)

        return sentFeatures
    
        #return " ".join([ ("%d:%d" % (f, sentFeatures[f]) )  for f in sorted(sentFeatures.keys())])



if __name__ == "__main__":

    import cPickle
    import avl

    with open("/home/james/tmp/combined/raw/cachedFeatures/ngrams_fold_0.pickle") as f:
        ngrams = cPickle.load(f)
        ngrams['bigram']  = avl.new(ngrams['bigram'])
        ngrams['unigram'] = avl.new(ngrams['unigram'])

    with open("/home/james/tmp/combined/raw/cachedFeatures/b105514n_mode2.Andrew.xml") as f:
        sents = cPickle.load(f)



    cats = []

    for sent in sents:
        cats.append(str(sent.corescLabel))

    svmenc = SVMLightEncoder(ngrams, )

    classes = sorted(list(set(cats)))

    for sent in sents:
        print classes.index(str(sent.corescLabel)) + 1, svmenc.encodeSentence(sent.candcFeatures)

