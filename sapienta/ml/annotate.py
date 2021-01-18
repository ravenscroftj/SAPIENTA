import os
import csv
import logging
import pickle
import crfsuite

from sapienta.ml.train import FeatureExtractorBase

class CRFAnnotator(FeatureExtractorBase):
    """This class can be used as a standalone sentence annotator
    """

    def __init__(self, modelFile, ngramsFile, cacheDir, features, config={}, logger=None):
        FeatureExtractorBase.__init__(self, modelFile, ngramsFile, cacheDir,
        features, config=config, logger=logger)


        #load ngrams
        self.logger.info("Loading cached ngrams from %s", self.ngramCacheFile)

        with open(self.ngramCacheFile, 'rb') as f:
                self.ngrams = pickle.load(f)
                self.ngrams['unigram'] = set(self.ngrams['unigram'])
                self.ngrams['bigram']  = set(self.ngrams['bigram'])

        self.logger.info("Ngram filter has %d bigrams and %d unigrams", 
                len(self.ngrams['bigram']), len(self.ngrams['unigram']))

        #load crfsuite
        self.tagger = crfsuite.Tagger()
        self.tagger.open(self.modelFile)
        

    #------------------------------------------------------------------------------------------------

    def annotate(self, file, marginal=False, probs=False):
        """Annotate the given input file with coresc labels"""

        sents = self.extractFeatures(file, cache=False)
        
        items, labels = self.crfdataForFeatures(sents)

        self.tagger.set(items)
        
        labels = list(self.tagger.viterbi())

        if probs:

            with open(file + ".probs.txt", "wb") as f:
                f.write(str(self.tagger.probability(labels)))

        if marginal:

            with open(file +".marginal.csv","wb") as f:

                csvw = csv.writer(f)

                csvw.writerow(['sid'] + sorted( list(self.tagger.labels()) ) )

                for i in range(len(sents)):
        
                    marginals = [ self.tagger.marginal(x,i) for x in self.tagger.labels() ]

                    csvw.writerow( [ i+1 ] + marginals)
                    

        return { s[0]: s[1] for s in zip([s.sid for s in sents],labels) }

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

    print (args)

    features = ['ngrams', 'verbs', 'verbclass','verbpos', 'passive','triples','relations','positions' ]


    anno = CRFAnnotator(args.modelFile, args.ngramsFile,
    os.path.join(os.path.dirname(args.paperFile), "cachedFeatures"), 
    features)

    anno.annotate(args.paperFile)

    print (args.paperFile,":",">".join(anno.annotate(args.paperFile)))

if __name__ == "__main__":
    
    logging.basicConfig(level=logging.INFO)
    
    rootlog = logging.getLogger()

    main()
        
