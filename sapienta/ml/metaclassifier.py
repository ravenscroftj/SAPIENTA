"""Meta-classifier that sits on top of CRF and decides how many tags to assign and which ones
"""

import theano

from lasagne.layers import *


ALL_CORESCS = ['Bac', 'Con', 'Exp', 'Goa', 'Hyp', 'Met', 'Mod', 'Mot', 'Obj', 'Obs', 'Res']


class MetaClassifier:

    def __init__(self):

        self.in_layer = InputLayer((None,None,len(ALL_CORESCS)))


    def test(self):
        pass

    def train(self):
        pass

    def label(self):
        pass

if __name__ == "__main__":
    print "Hello"
    m = MetaClassifier()
