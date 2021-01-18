import csv
import lxml.etree as ET
import os
import argparse

from itertools import product
from collections import Counter

#consensus_dir = "/home/james/Dropbox/CRA_corpus_Anika_Maria/code/Matrices/consensus"
consensus_dir = "/home/james/Dropbox/CRA_corpus_Anika_Maria/code/Matrices/PaperMatrix/mythili"
annotated_dir = "/home/james/Dropbox/CRA_corpus_Anika_Maria/crf_annotated"

all_labels = Counter()

total_sents = 0

lblcount = [0,0,0,0]

def load_consensus(cfile):

    global total_sents

    with open(cfile) as f:
        creader = csv.reader(f)

        for i,line in enumerate(creader):

            sid = 0
            labels = []
            
            if i == 0:
                headers = line
            else:


                if sum([float(x) for x in line[1:]]) == 0:
                    total = 0
                    lblcount[0] += 1
                else:
                    total = 1

                    for i, lbl in enumerate(line):
                        if i == 0:
                            sid = lbl
                        else:
                            if float(lbl) > 0:
                                lblcount[total] += 1
                                all_labels[headers[i]] += 1
                                labels.append( ( headers[i], lbl) )
                                total += 1

            if sid != 0:
                total_sents += 1
                yield sid, labels


def chunkify(fmap, n):
    """Break a set of lists of x items into approximately equal groups"""

    chunks = [ [] for i in range(n)]

    fvals = sorted( [ (k, len(item)) for k,item in list(fmap.items()) ], key=lambda x: x[1], reverse=True)

    for k, l in fvals:

        smallest = sorted(chunks, key=lambda x: sum([y for k,y in x]) )[0]

        smallest.append((k,l))

    return chunks


def generate_folds(consensus_dir, foldcount, foldfile):
    file_map = {}

    for root,dirs,files in os.walk(consensus_dir):

        for file in files:
            file_map[file] = list(load_consensus(os.path.join(root,file)))
            

    chunks = chunkify(file_map, foldcount)

    with open(foldfile,"w") as f:
        csvw = csv.writer(f)
        
        
        filecount = len(chunks)
        largest  = max([len(chunk) for chunk in chunks])
        
        print(largest)
        
        rowsize = 3 * foldcount + 1
        
        #generate title row
        titles = ['']*rowsize
        
        for i in range(0,foldcount):
                titles[i * 3 + 1] = "Fold {}".format(i+1)
        
        csvw.writerow(titles)
        
        #generate header row
        headers = [''] + (['filename', 'total_sentence','annotator'] * foldcount)
        
        csvw.writerow(headers)
        
        #generate rows
        for i in range(0, largest):
                
                row = [i+1]
                
                for fold in chunks:
                        if len(fold) <= i:
                                row += [0,0,'']
                        else:
                                row += [fold[i][0].replace("_mode2","")] + [fold[i][1]] + ['']
                                
                csvw.writerow(row)


def check_results():

    results = []

    for root,dirs,files in os.walk(consensus_dir):

        for file in files:
            gt = { x:y for x,y in load_consensus(os.path.join(root,file)) }

            tree = ET.parse(os.path.join(annotated_dir, file + "_annotated.xml"))


            for s in tree.iter("s"):
                coresc = s.find("CoreSc1")

                if coresc != None:

                    best = sorted(gt[s.get("sid")], key=lambda x: x[1], reverse=True)

                    if len(best) > 0:

                        for i, pair in enumerate(best):
                            lbl, conf = pair
                            results.append( (lbl, coresc.get("type"), i))


                    else:
                        results.append( (None, coresc.get("type"), None) )


    print("Total CoreSC tags: %d" % len(results))

    tot = 0

    for i in range(0,5):

        tot += len([ x for (x,y,z) in results if z == i and x==y ])

        print("Correct @ %d: %d" % (i+1, tot))

    labels = sorted(set([ y for x,y,z in results]))

    j = len(labels)

    lastx = None
    line = "," + ",".join(labels)

    for x,y in product(labels,repeat=2):

        if x != lastx:
            print(line)
            line = ""
            line += x

        line += ",%d" % len([ a for a,b,c in results if x==a and y==b ])

        lastx = x

    print(line)

if __name__ == "__main__":

    a = argparse.ArgumentParser()
    
    a.add_argument('folds', action='store', type=int, default=3,
            help='Number of folds to generate')

    a.add_argument('corpusdir', action='store', default=None,
            help='Directory in which xml papers are found. papers must be suffixed _mode2.xml')

    a.add_argument('--foldsfile', action='store', default='folds.csv',
            help='name of CSV file in which to store folds - defaults to folds.csv')

    args = a.parse_args()

    generate_folds(args.corpusdir, args.folds, args.foldsfile)

    #print total_sents

    #for lbl, num in all_labels.items():
    #    print lbl,num


    #for i,x in enumerate(lblcount):
    #	print (i+1),x
