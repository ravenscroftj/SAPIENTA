import csv
import lxml.etree as ET
import os

from itertools import product
from collections import Counter

annotated_dir = "/home/james/tmp/lrec16/new_crf"



def chunkify(fmap, n):
    """Break a set of lists of x items into approximately equal groups"""

    chunks = [ [] for i in range(n)]

    fvals = sorted( [ (k, item) for k,item in fmap.items() ], key=lambda x: x[1], reverse=True)

    for k, l in fvals:

        smallest = sorted(chunks, key=lambda x: sum([y for k,y in x]) )[0]

        smallest.append((k,l))

    return chunks


def generate_folds(corpus_dir):
    
    file_map = Counter()

    for root,dirs,files in os.walk(corpus_dir):

        if root.endswith("cachedFeatures"):
            continue

        for file in files:
            if file.endswith(".xml"):

                tree = ET.parse(os.path.join(root,file))
                for el in tree.iter("s"):
                    file_map[file] += 1


    for c in chunkify(file_map, 9):

        for entry in c:
            print "%s,%d" % entry
        print sum([x[1] for x in c])
        print "------------"


if __name__ == "__main__":

    generate_folds(annotated_dir)
