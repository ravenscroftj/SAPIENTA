"""Write contents of ngrams pickle to text files"""

pickle_file = "/home/james/tmp/combined/raw/cachedFeatures/ngrams_fold_0.pickle"
bi_file = "/home/james/tmp/bigrams.txt"
uni_file = "/home/james/tmp/unigrams.txt"

import pickle

print("extracting ngrams from pickle...")

with open(pickle_file,'rb') as f:
    
    ngrams = pickle.load(f)

print("writing bigrams...")

with open(bi_file,'wb') as f:

    for bi in ngrams['bigram']:
        f.write(bi + "\n")

print("writing unigrams...")

with open(uni_file, 'wb') as f:

    for u in ngrams['unigram']: 
        f.write(u + "\n")


