from __future__ import division

import sys
import os
import cPickle
import avl
import logging
import csv

from argparse import ArgumentParser
from collections import Counter

from sapienta.ml.train import CRFTrainer as Trainer

all_features = ['ngrams', 'verbs', 'verbclass','verbpos', 'passive','triples','relations','positions' ]

accum_fp = Counter()
accum_fn = Counter()
accum_tp = Counter()
accum_tf = Counter()

def calcPrecRecall(logger, resultFile, trueLabels, predictedLabels, probabilities):
    """Calculate precision and recall for sequences of true and predicted labels
    """

    labels = set(trueLabels).union(set(predictedLabels))
    tp = {}
    fp = {}
    fn = {}

    print labels

    f = open(resultFile,'wb')

    csvw = csv.writer(f)

    for label in labels:
        tp[label] = fp[label] = fn[label] = 0
    
    predictedZip = zip(predictedLabels, probabilities)
    
    logger.info("True label, Predicted Label, Probability")

    for true, predictedZip in zip(trueLabels, predictedZip):
        predictedLabel, probability = predictedZip
        logger.info("%s, %s, %s", true, predictedLabel, probability)
        if true == predictedLabel:
            tp[true] += 1
            accum_tp[true] += 1
        else:
            fp[predictedLabel] += 1
            fn[true] += 1

            accum_fp[predictedLabel] += 1
            accum_fn[true] += 1

    for label in labels:
        logger.info(label)
        if tp[label] == 0:
            prec = 0
            rec = 0
        else:
            prec = tp[label] / (tp[label] + fp[label])
            rec = tp[label] / (tp[label] + fn[label])
        
        if (prec + rec) > 0:
            fm = (2 * prec * rec ) / (prec + rec)
        else:
            fm = 0

        logger.info('prec: %d tp / (%d tp + %d fp) = %f', tp[label], tp[label], fp[label], prec)
        logger.info('rec: %d tp / (%d tp + %d fn) = %f', tp[label], tp[label], fn[label], rec)
        logger.info('F-measure: %f',fm)

        csvw.writerow([label, prec, rec, fm])

    totalSentences = sum(tp.values()) + sum(fp.values())

    rightpc = sum(tp.values()) * 100 /  totalSentences
    wrongpc = sum(fp.values()) * 100 /  totalSentences
    #write the accuracy
    csvw.writerow(["Classifier Accuracy", rightpc, wrongpc ])
    
    #close the csv file
    f.close()

if __name__ == "__main__":

    logger = logging.getLogger(__name__)

    logging.basicConfig(level=logging.INFO)
    
    
    a = ArgumentParser(description='Test a trained model and produce confusion matrix and micro-averages')
    

    a.add_argument('modelfile', action='store', default='all_papers.model',
            help='Path to the model file to evaluate')

    a.add_argument('ngramsfile', action='store', default='ngrams.pickle',
            help='Ngrams file to evaluate (should have been produced along side model)')

    a.add_argument('corpusdir', action='store', default=None,
            help='Directory in which xml papers are found and cached data can be stored.')

    a.add_argument('--resultfile', action='store', default='results.csv',
            help='name of CSV file in which to store results - defaults to results.csv')


    
    args = a.parse_args()

    if not os.path.exists(args.corpusdir):
        logger.error("Corpus dir %s does not exist. Please specify a valid directory", args.corpusdir)
        sys.exit(1)

    if not os.path.exists(args.modelfile):
        logger.error("Model file %s does not exist. Please specify a valid file", args.modelfile)
        sys.exit(1)

    if not os.path.exists(args.ngramsfile):
        logger.error("Ngrams file %s does not exist. Please specify a valid file", args.ngramsfile)
        sys.exit(1)

    cacheDir = os.path.join(args.corpusdir, "cachedFeatures")

    if not os.path.exists(cacheDir):
        os.mkdir(cacheDir)
        logger.info("Generating feature cache directory")


    t = Trainer(all_features, cacheDir, args.modelfile, args.ngramsfile, logger )

    testFiles = []

    for root, dirs, files in os.walk(args.corpusdir):

        if root.endswith("cachedFeatures"):
            continue

        testFiles.extend([ os.path.join(root,file) for file in files if file.endswith('.xml')])

    if len(testFiles) < 0:
        logger.error("No papers found in %s - stopping.", a.corpusdir)
        sys.exit(1)


    results = t.testModel(testFiles)

    calcPrecRecall(logger, args.resultfile, *results)
