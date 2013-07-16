"""A set of tools and utilities for producing SVMLight compatible sentence data
"""

class SVMLightEncoder:


    def __init__(self, ngrams, classes):

        self.classes = sorted(classes)
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

    svmenc = SVMLightEncoder(ngrams, list(set(cats)))

    for sent in sents:
        print svmenc.getCatID(sent.corescLabel), svmenc.encodeSentence(sent.candcFeatures)

