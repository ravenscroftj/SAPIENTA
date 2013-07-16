"""A set of tools and utilities for producing SVMLight compatible sentence data
"""

from sapienta.ml.train import SAPIENTATrainer

class SVMLightTrainer(SAPIENTATrainer):
    """SAPIENTA trainer that produces SVMLight formatted training/testing data
    """


    def train(self, trainfiles):
        self.preprocess(trainfiles)

        encoder = SVMLightEncoder(self.ngrams)

        all_sents = {}

        for file in trainfiles:
            sents = self.extractFeatures(file)

            for sent in sents:
                label = sent.corescLabel
                encoded = encoder.encodeSentence(sent.candcFeatures)

                if not label in all_sents:
                    all_sents[label] = []

                all_sents[label].append(encoded)

            
            
#---------------------------------------------------------------------------------------

class SVMLightEncoder:

    def __init__(self, ngrams):

        self.ngrams = ngrams

    def encodeSentence(self, candcSentence):
        """Given a sentence, return svmlight syntax for features within it
        """

        baseFeatureIndex = 1
        
        sentFeatures = []

        for label, ngrams in {'unigram' : candcSentence.unigrams, 'bigram':candcSentence.bigrams }.items():

            for ngram in ngrams:
                idx = self.ngrams[label].index(ngram)

                if idx > -1:
                    sentFeatures.append(idx + baseFeatureIndex)

            baseFeatureIndex += len(ngrams)
    
        return " ".join([ ("%d:1" % f) for f in sentFeatures] )

    def getCatID( self, catname ):
        return self.classes.index(str(catname)) + 1



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

