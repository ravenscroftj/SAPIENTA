"""
Given the path to a set of 'cached features', rebuild the ngrams in the cache
"""
import os
import cPickle
import logging
import sys

from sapienta.ml.train import FeatureExtractorBase:



features = ['ngrams', 'verbs', 'verbclass','verbpos', 'passive','triples','relations','positions' ]

def main():
    """This is where the magic happens"""

    from argparse import ArgumentParser


    a = ArgumentParser(description='Build an ngrams model from a set of papers')

    a.add_argument("papersDirectory", help="Where papers to build ngrams model from are stored.")


    logging.basicConfig(level=logging.INFO)


    logger = logging.getLogger("rebuild_ngrams:main")


    cachePath = os.path.join(papersDir, "cachedFeatures")


    FExtractor = FeatureExtractorBase("", "", cacheDir, features )

    if not os.path.exists(cachePath):
        logger.info("Creating cache dir at " + cachePath)
        os.makedirs(cachePath)

    featFiles = [ f for f in os.listdir(papersDir) of f.endswith(".xml") ]

    for file in featFiles:

        cacheFile = os.path.join(cachePath,file)
        
        if os.path.exists(cacheFile):
 
            logger.info("Loading cached features from %s", cacheFile)

            with open(cacheFile,'rb') as f:
                features = cPickle.load(f)

        else:
            logger.info("Extracting features from %s", file)
            features = FExtractor.extractFeatures(file)

        logger.info("Processing file %s", file)

        logger.info("Found %d sentences", len(features))

        for sent in features:
            cf = sent.candcFeatures
            cf.unigrams, cf.bigrams, cf.trigrams = cf.createNgrams(cf.tokens)

        logger.info("Writing changes back to %s", file)

        with open(file, 'wb') as f:
            cPickle.dump(features, f)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    main()
