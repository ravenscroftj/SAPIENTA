from __future__ import division

import avl
import logging
import os
import crfsuite
import cPickle
import csv

from multiprocessing import Pool, Lock

from sapienta.ml.train import SAPIENTATrainer

from collections import Counter


def train_and_test(fixture):
    """This method creates a trainer and trains and evaluates a crf model
    """

    features, cacheDir, corpusDir, foldNo, testFiles, trainFiles, lock = fixture

    ngramCacheFile = os.path.join(cacheDir, "ngrams_fold_%d.pickle" % foldNo)
    
    modelPath = os.path.join(corpusDir, 
            "model_fold_%d.model" % foldNo)

    logger = logging.getLogger(__name__ + ":trainer:fold_%d" % foldNo)
    
    logger.addHandler(logging.FileHandler(os.path.join(corpusDir, "logs", "fold_%d.log" % foldNo)))

    #construct a sapienta trainer object
    trainer = SAPIENTATrainer(features, cacheDir, modelPath, ngramCacheFile, logger)

    if os.path.exists(modelPath):
        logger.warn("Not regenerating model for fold %d. "
                "Rename the model file to force regeneration", foldNo)
    else:
        trainer.train(trainFiles)

    #test the model - newly trained or otherwise 
    logger.info("Testing model from fold %d", foldNo)
    return trainer.testModel(testFiles)

    

class CrossValidationTrainer:

    def __init__(self):
        """Create a cross validating trainer using SAPIENTA trainer as a backend"""
        self.logger = logging.getLogger(__name__)

        
        self.accum_tp = Counter()
        self.accum_fp = Counter()
        self.accum_fn = Counter()

    #------------------------------------------------------------------------------------------------

    def train_cross_folds( self, foldsFile, corpusDir, features):
        """Train SAPIENTA on folds described in foldsFile."""

        from sapienta.ml.folds import get_folds
        
        self.folds = get_folds( foldsFile )
        self.corpusDir = corpusDir

        if not os.path.exists(os.path.join(corpusDir, "logs")):
            os.makedirs(os.path.join(corpusDir, "logs"))

        self.logger.addHandler(logging.FileHandler(os.path.join(corpusDir, 
            "logs", "folds_all.log")))

        self.cacheDir = os.path.join(self.corpusDir, "cachedFeatures")

        if not os.path.exists(self.cacheDir):
            os.mkdir(self.cacheDir)
            self.logger.info("Generating feature cache directory")

        genFileName = lambda x: os.path.join(corpusDir, x['filename'] + 
                                    "_mode2." + x['annotator'] + ".xml")


        allFiles =  [f for f in [ genFileName(fdict) 
                        for x in self.folds for fdict in x ] 
                                    if os.path.exists(f)]
    
        fixtures = []

        for f, fold in enumerate(self.folds):

            testFiles = []
            sents = 0
            
            for filedict in fold:
                fname = os.path.join(corpusDir, filedict['filename'] + "_mode2." + 
                        filedict['annotator'] + ".xml")

                sents += int(filedict['total_sentence'])

                if not os.path.isfile(fname):
                    self.logger.warn("No file %s detected.", fname)
                else:
                    testFiles.append(fname)

            self.logger.info("Fold %d has %d files and %d sentences total" + 
                    " (which will be excluded)", f, len(testFiles), sents)

            #calculate which files to use for training
            trainFiles = [file for file in allFiles if file not in testFiles]

            fixtures.append( ( features, self.cacheDir, self.corpusDir, f, testFiles, trainFiles,None))
            

        p = Pool()
        
        #run the training
        results = map(train_and_test, fixtures)

        #calculate and show results for folds
        for f,r in enumerate(results):
            self.calcPrecRecall(f,*r)

        #now show total microaverages for models
        self.calcMicroAverages()

    #------------------------------------------------------------------------------------------------

    def calcPrecRecall(self, fold, trueLabels, predictedLabels, probabilities):
        """Calculate precision and recall for sequences of true and predicted labels
        """
        labels = set(trueLabels).union(set(predictedLabels))
        tp = {}
        fp = {}
        fn = {}

        f = open(os.path.join(self.corpusDir, "results_fold_%d.csv" % fold))
        csvw = csv.writer(f)

        for label in labels:
            tp[label] = fp[label] = fn[label] = 0
        
        predictedZip = zip(predictedLabels, probabilities)
        #self.logger.info("True label, Predicted Label, Probability")

        for true, predictedZip in zip(trueLabels, predictedZip):
            predictedLabel, probability = predictedZip
            #self.logger.info("%s, %s, %s", true, predictedLabel, probability)
            if true == predictedLabel:
                tp[true] += 1
                self.accum_tp[true] += 1
            else:
                fp[predictedLabel] += 1
                fn[true] += 1

                self.accum_fp[predictedLabel] += 1
                self.accum_fn[true] += 1

        for label in labels:
            self.logger.info(label)
            if tp[label] == 0:
                prec = 0
                rec = 0
            else:
                prec = tp[label] / (tp[label] + fp[label])
                rec = tp[label] / (tp[label] + fn[label])
            
            fm = (2 * prec * rec ) / (prec + rec)
            
            self.logger.info('prec: %d tp / (%d tp + %d fp) = %f', tp[label], tp[label], fp[label], prec)
            self.logger.info('rec: %d tp / (%d tp + %d fn) = %f', tp[label], tp[label], fn[label], rec)
            self.logger.info('F-measure: %f',fm)

            csvw.writerow([label, prec, rec, fm])

        
        #close the csv file
        f.close()


    #------------------------------------------------------------------------------------------------

    def calcMicroAverages(self):
        """Calculate microaverages for precision recall and f-measure across all 9 folds
        """


        f = open(os.path.join(self.corpusDir, "micro_all.csv"))

        csvw = csv.writer(f)

        for label in self.accum_tp:
            self.logger.info(label)
            if self.accum_tp[label] == 0:
                prec = 0
                rec = 0
            else:
                prec = self.accum_tp[label] / (self.accum_tp[label] + self.accum_fp[label])
                rec = self.accum_tp[label] / (self.accum_tp[label] + self.accum_fn[label])

            fm = (2 * prec * rec ) / (prec + rec)

            self.logger.info('prec: %d tp / (%d tp + %d fp) = %f', self.accum_tp[label], self.accum_tp[label], self.accum_fp[label], prec)
            self.logger.info('rec: %d tp / (%d tp + %d fn) = %f', self.accum_tp[label], self.accum_tp[label], self.accum_fn[label], rec)
            self.logger.info('F-measure: %f',fm)

            #write csv result
            csvw.writerow([label, prec, rec, fm])
        
        #close the writer
        f.close()

    
#------------------------------------------------------------------------------------------------

def main():
    """Main entrypoint for cross validation training script"""

    t = CrossValidationTrainer()
    #features = ['ngrams', 'verbs', 'verbclass','verbpos', 'passive','triples','relations','positions' ]
    features = ['ngrams']
    t.train_cross_folds("/home/james/tmp/foldTable.csv", "/home/james/tmp/combined/raw", features)


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    
    rootlog = logging.getLogger()



    main()
        
