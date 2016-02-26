"""Meta-classifier that sits on top of CRF and decides how many tags to assign and which ones
"""

import theano
import time
import csv
import os
import lasagne
import sys
import logging
import theano.tensor as T
import numpy as np

from lasagne.layers import *


ALL_CORESCS = ['Bac', 'Con', 'Exp', 'Goa', 'Hyp', 'Met', 'Mod', 'Mot', 'Obj', 'Obs', 'Res']

N_HIDDEN = 50

# Optimization learning rate
LEARNING_RATE = .01

# How often should we check the output?
EPOCH_SIZE = 100

class MetaClassifier:

    def __init__(self):

        self.logger = logging.getLogger(__name__)

        self.logger.info("Creating theano neural network")

        self.in_layer = InputLayer((None,None,len(ALL_CORESCS)))

        self.i_mask = InputLayer((None,None))

        batchsize,seqlen, _ = self.in_layer.input_var.shape

        l_lstm = LSTMLayer(self.in_layer, num_units=N_HIDDEN, mask_input=self.i_mask, nonlinearity=lasagne.nonlinearities.tanh)
        l_back_lstm =  LSTMLayer(self.in_layer, num_units=N_HIDDEN, mask_input=self.i_mask, nonlinearity=lasagne.nonlinearities.tanh,backwards=True)


        l_merge = ElemwiseSumLayer([l_lstm,l_back_lstm])


        l_lstm2 = LSTMLayer(l_merge, num_units=len(ALL_CORESCS), mask_input=self.i_mask, nonlinearity=lasagne.nonlinearities.tanh)

        l_shp = ReshapeLayer(l_lstm2, (-1, len(ALL_CORESCS)))

        l_dense = DenseLayer(l_shp, num_units=len(ALL_CORESCS), nonlinearity=lasagne.nonlinearities.sigmoid)

        self.l_out = ReshapeLayer(l_dense, ( batchsize,seqlen, len(ALL_CORESCS) ) )

        target_values = T.dtensor3('target_values')

        network_output = lasagne.layers.get_output(self.l_out)

        # The loss function is calculated as the mean of the (categorical) 
        # cross-entropy between the prediction and target.
        #cost = T.mean( (network_output - target_values) ** 2)
        cost = T.nnet.categorical_crossentropy(network_output,target_values).mean()

        # Retrieve all parameters from the network
        all_params = lasagne.layers.get_all_params(self.l_out,trainable=True)

        self.logger.info("Computing updates...")
        updates = lasagne.updates.nesterov_momentum(cost, all_params, LEARNING_RATE)

        # Theano functions for training and computing cost
        self.logger.info("Compiling functions ...")

        self.train = theano.function([self.in_layer.input_var, target_values, self.i_mask.input_var], cost, 
                updates=updates, allow_input_downcast=True)

        self.compute_cost = theano.function([self.in_layer.input_var, target_values, self.i_mask.input_var], cost, 
                allow_input_downcast=True)

        self.label = theano.function([self.in_layer.input_var, self.i_mask.input_var],network_output,allow_input_downcast=True)


    def test(self):
        pass



def load_csv_file(cfile):

    with open(cfile) as f:
        creader = csv.reader(f)

        for i,line in enumerate(creader):

            sid = 0
            labels = []
            
            if i == 0:
                headers = line
            else:
                for i, lbl in enumerate(line):
                    if i == 0:
                        sid = lbl
                    else:
                        if float(lbl) > 0:
                            labels.append( ( headers[i], lbl) )

            if sid != 0:
                yield sid, labels


def load_ground_truth(dir):

    for root,dirs,files in os.walk(dir):

        for file in files:
            gt = load_csv_file(os.path.join(root,file))
            yield file,gt


def csv_to_nnet(gt):
    """Munge CSV formatted data into neural network input or output"""
    gt = list(gt)
    seq =  np.zeros( (len(gt), len(ALL_CORESCS)) )

    for i, (sid, labels) in enumerate(gt):

        #if sum([ score for lbl,score in labels]) == 0
        #    print("Skipping sid {} which has values {}".format(sid,repr(labels)) )
        #    continue

        for lbl,score in labels:
            if lbl == '': continue
            seq[i][ALL_CORESCS.index(lbl)] = score
        
    return seq

def main():
    from argparse import ArgumentParser

    a = ArgumentParser(description='Train, test and use a metaclassifier on CRF marginals')

    a.add_argument('action', choices=['test','train','use'])

    a.add_argument('marginals_dir', action='store', default=None,
            help="CSV files that detail marginal values from CRF")

    a.add_argument('gt_dir', action='store',
        help='Location of CSV ground truth for paper labels')

    a.add_argument('--model', action='store', default='model.npz', help='Set the name of the neural network model file to save to write')

    a.add_argument('--continue', dest='continue_training', action='store', default=None, help='Try to read the model file specified and continue training')

    a.add_argument('--epochs', action='store', default=1000, type=int, help='Number of training epochs before halting and writing model to disk.')

    args = a.parse_args()


    ys = []
    xs = []
    files = []

    for filename, gt in  load_ground_truth(args.gt_dir):

        ys.append(csv_to_nnet(gt))

        marginals = load_csv_file(os.path.join(args.marginals_dir, filename +"_split.xml.marginal.csv"))

        xs.append(csv_to_nnet(marginals))
        files.append(filename)


    max_sents_x = max( [len(x) for x in xs] )
    max_sents_y = max( [len(y) for y in ys] )

    np_xs = np.zeros( (len(xs),max_sents_x,len(ALL_CORESCS)  ), dtype='float64' )
    np_ys = np.zeros( (len(ys),max_sents_y,len(ALL_CORESCS)  ), dtype='float64' )
    np_masks = np.zeros( (len(ys),max_sents_y ), dtype='float64' )
    
    for i,x in enumerate(xs):
        np_xs[i, :x.shape[0], :x.shape[1] ]= x
        np_masks[i, :x.shape[0] ]= 1

    for i,y in enumerate(ys):
        np_ys[i, :y.shape[0], :y.shape[1] ]= y


    m = MetaClassifier()

    if args.continue_training != None:
        print("Loading model and continuing training...")
        with np.load(args.continue_training) as f:
            param_values = [f['arr_%d' % i] for i in range(len(f.files))]

        lasagne.layers.set_all_param_values(m.l_out, param_values)

    val_x = np_xs[:1]
    val_y = np_ys[:1]
    val_masks = np_masks[:1]

    train_x = np_xs[1:40]
    train_y = np_ys[1:40]
    train_masks = np_masks[1:40]

    test_x = np_xs[40:]
    test_y = np_ys[40:]
    test_masks = np_masks[40:]
    test_files = files[40:]

    print("Starting training")

    for epoch in range(args.epochs):

        start = time.clock()

        #for _ in range(100):
        m.train(train_x, train_y, train_masks)

        cost_val = m.compute_cost(val_x,val_y,val_masks)

        end = time.clock()

        print("Epoch {} validation cost = {}  ({} seconds)").format(epoch,cost_val,end-start)

    
    rs = m.label(test_x, test_masks)


    with open("results.pickle", "wb") as f:
        import cPickle
        cPickle.dump(zip(rs,test_files),f)


    print("Saving model...")


    
    model_values = lasagne.layers.get_all_param_values(m.l_out)

    #for file, results in zip(rs, test_files):
    #    print file

    np.savez('model.npz', *lasagne.layers.get_all_param_values(m.l_out))
        




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
