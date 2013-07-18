import avl
import os
import logging
import cPickle
import crfsuite

from sapienta.ml.train import FeatureExtractorBase

class CRFAnnotator(FeatureExtractorBase):
    """This class can be used as a standalone sentence annotator
    """

    def __init__(self, modelFile, ngramsFile, cacheDir, features):
        FeatureExtractorBase.__init__(self, modelFile, ngramsFile, cacheDir,
        features)


        #load ngrams
        self.logger.info("Loading cached ngrams from %s", self.ngramCacheFile)

        with open(self.ngramCacheFile, 'rb') as f:
                self.ngrams = cPickle.load(f)
                self.ngrams['unigram'] = avl.new(self.ngrams['unigram'])
                self.ngrams['bigram']  = avl.new(self.ngrams['bigram'])

        self.logger.info("Ngram filter has %d bigrams and %d unigrams", 
                len(self.ngrams['bigram']), len(self.ngrams['unigram']))

        #load crfsuite
        tagger = crfsuite.Tagger()
        tagger.open(self.modelFile)
        tagger.set(items)
        

    #------------------------------------------------------------------------------------------------

    def annotate(self, file):
        """Annotate the given input file with coresc labels"""

        sents = self.extractFeatures(file, cache=False)
        
        items, labels = self.crfdataForFeatures(sents)


        return tagger.viterbi()

#------------------------------------------------------------------------------------------------
def main():
    """Main entrypoint for annotator script"""

    from argparse import ArgumentParser

    a = ArgumentParser(description='Use a trained model to annotate a document')

    a.add_argument('--features', dest='features', action='store', default=None,
            help="List of features used in training separated by commas.")


    a.add_argument('modelFile', metavar='model_file',
        help='The file in which the trained model is stored')

    a.add_argument('ngramsFile', metavar='ngrams_file',
        help='The file in which the ngrams can be found.')

    a.add_argument('paperFile', metavar='paper_file',
        help='Name of the file to be annotated')

    args = a.parse_args()

    print args

    features = ['ngrams', 'verbs', 'verbclass','verbpos', 'passive','triples','relations','positions' ]


    anno = CRFAnnotator(args.modelFile, args.ngramsFile,
    os.path.join(os.path.dirname(args.paperFile), "cachedFeatures"), 
    features)

    anno.annotate(args.paperFile)

if __name__ == "__main__":
    
    logging.basicConfig(level=logging.INFO)
    
    rootlog = logging.getLogger()

    main()
        
