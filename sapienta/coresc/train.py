"""Entrypoint and utility functions for training SAPIENTA model
"""

import logging

class SAPIENTATrainer:

    def __init__(self):
        """Create a sapienta trainer object"""
        self.logger = logging.getLogger(__name__)

    def train_cross_folds( self, foldsFile, corpusDir):]
        """Train SAPIENTA on folds described in foldsFile."""

        from sapienta.coresc.folds import get_folds
        
        self.folds = get_folds( foldsFile )
        self.corpusDir = corpusDir


        
