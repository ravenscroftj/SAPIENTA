from __future__ import division

import sys
import logging
import os
import crfsuite
import pickle
import csv

from multiprocessing import Pool, Lock

#from sapienta.ml.svmlight import SVMLightTrainer as Trainer
from sapienta.ml.train import CRFTrainer as Trainer
from sapienta.ml.folds import get_folds
from collections import Counter



def train_and_test(fixture):
    """This method creates a trainer and trains and evaluates a crf model
    """

    modelType, features, cacheDir, corpusDir, foldNo, testFiles, trainFiles, lock = fixture

    ngramCacheFile = os.path.join(cacheDir, "ngrams_fold_%d.pickle" % foldNo)
    
    modelPath = os.path.join(corpusDir, 
            "model_fold_%d_%s.model" % (foldNo,modelType))

    logger = logging.getLogger(__name__ + ":trainer:fold_%d" % foldNo)
    
    logger.addHandler(logging.FileHandler(os.path.join(corpusDir, "logs", "fold_%d.log" % foldNo)))

    logger.info("Training model of type %s", modelType)

    if modelType == 'crf':
        from sapienta.ml.train import CRFTrainer as Trainer
    elif modelType == 'svm':
        from sapienta.ml.svmlight import SVMLightTrainer as Trainer
    else:
        logger.error("Unknown model type %s", modelType)
        sys.exit()

    #construct a sapienta trainer object
    trainer = Trainer(features, cacheDir, modelPath, ngramCacheFile, logger)

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

    def train_cross_folds( self, modelType, corpusDir, features, foldsFile=None, loo=False ):
        """Train SAPIENTA on folds described in foldTable."""

        
        
        self.modelType = modelType

        if foldsFile == None and not loo:
            self.logger.error("You must either specify --leave-one-out or --foldTable=filename.csv")
            return

        if foldsFile != None:
            self.folds = get_folds( foldsFile )
        else:
            self.folds = None
        
        self.corpusDir = corpusDir

        if not os.path.exists(os.path.join(corpusDir, "logs")):
            os.makedirs(os.path.join(corpusDir, "logs"))

        self.logger.addHandler(logging.FileHandler(os.path.join(corpusDir, 
            "logs", "folds_all.log")))

        self.cacheDir = os.path.join(self.corpusDir, "cachedFeatures")

        if not os.path.exists(self.cacheDir):
            os.mkdir(self.cacheDir)
            self.logger.info("Generating feature cache directory")


        def genFileName(x):
            if x['annotator'] != "":
                return os.path.join(corpusDir, x['filename'] + 
                                    "_mode2." + x['annotator'] + ".xml") 
            else:
                return os.path.join(corpusDir, x['filename'] + 
                                    "_mode2.xml")


    
        fixtures = []


        if self.folds != None:

            #TEMPORARY THING THAT STOPS LOOKING AFTER 3 FOLDS
            #self.folds = self.folds[:1]


            allFiles =  [f for f in [ genFileName(fdict) 
                        for x in self.folds for fdict in x ] 
                                    if os.path.exists(f)]

            for f, fold in enumerate(self.folds):

                testFiles = []
                sents = 0
                
                for filedict in fold:
                    fname = genFileName(filedict)

                    sents += int(filedict['total_sentence'])

                    if not os.path.isfile(fname):
                        self.logger.warn("No file %s detected.", fname)
                    else:
                        testFiles.append(fname)

                self.logger.info("Fold %d has %d files and %d sentences total" + 
                        " (which will be excluded)", f, len(testFiles), sents)

                #calculate which files to use for training
                trainFiles = [file for file in allFiles if file not in testFiles]

                fixtures.append( ( self.modelType, features, self.cacheDir, self.corpusDir, f, testFiles, trainFiles,None))

        else: #else we do leave-one-out instead of folds

            allFiles = []

            for root, dirs, files in os.walk(self.corpusDir):

                if root.endswith("cachedFeatures"):
                    continue

                for file in files:
                    if file.endswith(".xml"):
                        allFiles.append(os.path.join(root,file))

            #generate leave-one-out fixtures
            for i, file in enumerate(allFiles):
                trainFiles = allFiles[0:i] + allFiles[i+1:]
                testFiles = [file]

                fixtures.append( (self.modelType, features, self.cacheDir, self.corpusDir, i, testFiles, trainFiles, None))

        
        #run the training
        p = Pool()
        results = p.map(train_and_test, fixtures)
        #results = map(train_and_test, fixtures)

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

        print (labels)

        f = open(os.path.join(self.corpusDir, "results_fold_%d.csv" %
        fold),'w')

        csvw = csv.writer(f)

        for label in labels:
            tp[label] = fp[label] = fn[label] = 0
        
        predictedZip = zip(predictedLabels, probabilities)
        
        self.logger.info("True label, Predicted Label, Probability")

        for true, predictedZip in zip(trueLabels, predictedZip):
            predictedLabel, probability = predictedZip
            self.logger.info("%s, %s, %s", true, predictedLabel, probability)
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
            
            if (prec + rec) > 0:
                fm = (2 * prec * rec ) / (prec + rec)
            else:
                fm = 0

            self.logger.info('prec: %d tp / (%d tp + %d fp) = %f', tp[label], tp[label], fp[label], prec)
            self.logger.info('rec: %d tp / (%d tp + %d fn) = %f', tp[label], tp[label], fn[label], rec)
            self.logger.info('F-measure: %f',fm)

            csvw.writerow([label, prec, rec, fm])

        totalSentences = sum(tp.values()) + sum(fp.values())

        rightpc = sum(tp.values()) * 100 /  totalSentences
        wrongpc = sum(fp.values()) * 100 /  totalSentences
        #write the accuracy
        csvw.writerow(["Classifier Accuracy", rightpc, wrongpc ])
        
        #close the csv file
        f.close()


    #------------------------------------------------------------------------------------------------

    def calcMicroAverages(self):
        """Calculate microaverages for precision recall and f-measure across all 9 folds
        """


        f = open(os.path.join(self.corpusDir, "micro_all.csv"),'wb')

        csvw = csv.writer(f)

        for label in self.accum_tp:
            self.logger.info(label)
            if self.accum_tp[label] == 0:
                prec = 0
                rec = 0
            else:
                prec = self.accum_tp[label] / (self.accum_tp[label] + self.accum_fp[label])
                rec = self.accum_tp[label] / (self.accum_tp[label] + self.accum_fn[label])

            if (prec + rec) > 0:
                fm = (2 * prec * rec ) / (prec + rec)
            else:
                fm = 0

            self.logger.info('prec: %d tp / (%d tp + %d fp) = %f', self.accum_tp[label], self.accum_tp[label], self.accum_fp[label], prec)
            self.logger.info('rec: %d tp / (%d tp + %d fn) = %f', self.accum_tp[label], self.accum_tp[label], self.accum_fn[label], rec)
            self.logger.info('F-measure: %f',fm)

            #write csv result
            csvw.writerow([label, prec, rec, fm])
        
        totalSentences = sum(self.accum_tp.values()) + sum(self.accum_fp.values())
        rightpc = sum(self.accum_tp.values()) * 100 /  totalSentences
        wrongpc = sum(self.accum_fp.values()) * 100 /  totalSentences
        #write the accuracy
        csvw.writerow(["Classifier Accuracy", rightpc, wrongpc ])
        
        #close the writer
        f.close()

    
#------------------------------------------------------------------------------------------------

def main():
    """Main entrypoint for cross validation training script"""

    import sys
    from argparse import ArgumentParser
    
    a = ArgumentParser(description='Cross-validate sentence annotator models')
    
    a.add_argument('--features', dest='features', action='store', default=None,
            help="List of features used in training separated by commas.")

    a.add_argument('--foldTable', dest='foldTable', default=None, metavar='fold_table_path', type=str,help='')

    a.add_argument('--leave-one-out', dest='loo', action="store_true")

    a.add_argument('--model', dest='modeltype', action='store', default='crf',
            help='The type of model to train - crf or svm - defaults to crf')

    a.add_argument('corpusdir', action='store', default=None,
            help='Directory in which xml papers are found and cached data can be stored.')

    
    t = CrossValidationTrainer()
    
    args = a.parse_args()


    all_features = ['ngrams', 'verbs', 'verbclass','verbpos', 'passive','triples','relations','positions' ]

    if args.features == None:
        logging.info("Using all features for training: %s", ",".join(all_features))
        features = all_features
    else:
        for f in args.features.split(","):
            if f not in all_features:
                logging.error("Unknown feature: %s, valid features are %s", f, ",".join(all_features))
                sys.exit(1)

        features = args.features


    if args.foldTable == None and not args.loo:
        logging.error("You must either specify --leave-one-out or --foldTable=filename.csv")
        sys.exit(1)

    #make sure the fold table exists
    if not ( args.loo or os.path.isfile(args.foldTable)):
        logging.error("Invalid fold table given %s", args.foldTable)
        sys.exit(1)

    if args.corpusdir != None:
        corpusdir = args.corpusdir
    else:
        logging.warn("No corpusdir specified, using fold table directory")
        corpusdir = os.path.dirname(args.foldTable)

    if not os.path.isdir(corpusdir):
        logging.error("Invalid corpus dir %s, specify an existing directory", corpusdir)
        sys.exit(1)

    
    t.train_cross_folds(args.modeltype, corpusdir, features,  args.foldTable, args.loo)
    #t.train_cross_folds("/home/james/tmp/foldTable.csv", "/home/james/tmp/combined/raw", features)



if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    rootlog = logging.getLogger()
    main()
        
