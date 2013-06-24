"""Entrypoint and utility functions for training SAPIENTA model
"""

import os
import logging

class SAPIENTATrainer:

    def __init__(self):
        """Create a sapienta trainer object"""
        self.logger = logging.getLogger(__name__)

    def train_cross_folds( self, foldsFile, corpusDir):
        """Train SAPIENTA on folds described in foldsFile."""

        from sapienta.ml.folds import get_folds
        
        self.folds = get_folds( foldsFile )
        self.corpusDir = corpusDir

        for f, fold in enumerate(self.folds):

            files = []
            sents = 0
            
            for filedict in fold:
                fname = os.path.join(corpusDir, filedict['filename'] + "_mode2." + filedict['annotator'] + ".xml")

                sents += int(filedict['total_sentence'])

                if not os.path.isfile(fname):
                    self.logger.warn("No file %s detected.", fname)
                else:
                    files.append(fname)

            self.logger.info("Fold %d has %d files and %d sentences total", f, len(files), sents)

             



def main():
    """Main entrypoint for training script"""

    t = SAPIENTATrainer()
    t.train_cross_folds("/home/james/tmp/foldTable.csv", "/home/james/tmp/combined/raw")


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    main()
        
