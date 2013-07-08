"""
Given the path to a set of 'cached features', rebuild the ngrams in the cache
"""
import os
import cPickle
import logging


def main():
    """This is where the magic happens"""

    logger = logging.getLogger("rebuild_ngrams:main")

    cachePath = "/home/james/tmp/combined/raw/cachedFeatures"

    featFiles = []

    for root, dirs, files in os.walk(cachePath):

        for file in files:
            if file.endswith(".xml"):
                featFiles.append(os.path.join(root, file))

    for file in featFiles:
        
        logger.info("Processing file %s", file)

        with open(file,'rb') as f:
            features = cPickle.load(f)

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
