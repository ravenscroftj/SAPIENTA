'''
Created on 20 Jul 2015

@author: James Ravenscroft
'''
import os
import re
import cPickle
import multiprocessing
from lxml import etree as ET

from sapienta.tools.sssplit import referenceElements, commonAbbreviations,\
    highLevelContainerElements, pLevelContainerElements

from nltk import MaxentClassifier as Classifier
#from nltk import NaiveBayesClassifier as Classifier
#from nltk.classify.decisiontree import DecisionTreeClassifier as Classifier

def is_str(s):
    return isinstance(s,str) or isinstance(s,unicode)


def extract_plevel_text(filename):
    """Return a list of text tokens intermingled with relevent elements in a p-level container"""
    
    tree = ET.parse(filename)
    root = tree.getroot()
    
    plevels = []
    
    for container in highLevelContainerElements:
        for containerEl in root.iter(container):
            
            for containerType in pLevelContainerElements:
                for el in set(containerEl.findall(containerType)):
                    siblings = list(el)
                    #if the container element has text insert in front of other siblings
                    if el.text != None:
                        siblings = [ el.text] + siblings
                    
                    plevels.append(siblings)
    
    for p in plevels:
        for node in p:
            if is_str(node):
                yield node.strip().split(" ")
            else:
                tail = node.tail
                node.tail = None
                yield node
                
                if tail != None:
                    yield tail.strip().split(" ")
            
def extract_sentences(file):
    
    tree = ET.parse(file)
    root = tree.getroot()
    
    sentences = []
    
    for el in root.iter('S','s'):
        sent = []
        
        if el.text != None:
            sent.extend(el.text.strip().split(" "))
        
        for node in el:
            tail = node.tail
            node.tail = None
            sent.append(node)
            if tail != None:
                sent.extend(tail.strip().split(" "))
        
        sentences.append(sent)
        
    return sentences

def text_to_features(tokenlist):
    """Turns a tokenlist into machine learning features"""

    prevRef = False
    nextRef = False
    prevTok = None
    
    tokenlist = [ (i, x) for i,x in enumerate(tokenlist) if x != ""]
        
    while len(tokenlist) > 0:
        #get first token
        i,tok = tokenlist.pop(0)
        
        if len(tokenlist) > 0:
            j,next = tokenlist[0]
        else:
            next = None
            
        if not is_str(next) and next != None:
            nextRef = next.tag in referenceElements
            next = None
        
        if is_str(tok):
            
            yield { 'hasPeriod' : tok.endswith('.'), 
                   'hasExclamation' : tok.endswith('!'),
                   'hasQuestion' : tok.endswith('?'),
                   'endBracket' : re.match("\]\)$", tok) != None,
                   'caps': tok.isupper(),
                   'lower': tok.islower(), 
                   'title': tok.istitle(),
                   'abbr' : tok.strip(".,()[]") in commonAbbreviations,
                   'next' : next,
                   'prev' : prevTok,
                   'len' : len(tok),
                   'probablyAbbr': re.match("([A-Z0-9]\.)+$", tok) != None,
                   'prevRef' : prevRef,
                   'nextRef' : nextRef,
                   'tok(%s)' % tok.strip(".,()[]") : True
                   } 
            
            prevTok = tok
        
        #if this element is a reference, set 'prevref' and continue
        elif tok.tag in referenceElements:
            prevRef = True
            yield{ 'isReference': True, 'prev' : prevTok }
            prevTok = "REF"
        else:
            yield {}
            
def sentence_to_features(sentence):
    features = []
    
    tokfeatures = list(text_to_features(sentence))
    
    if(len(tokfeatures) < 1):
        return []
    
    for f in tokfeatures[1:-1]:
        features.append( (f,False) )
        
    features.append( (tokfeatures[-1], True) )
    
    return features

def get_file_training_features(filename):
    sents = extract_sentences(filename)
    
    return reduce(lambda x,y: x + y, [ sentence_to_features(s) for s in sents ])

    
if __name__ == "__main__":
    
    TRAIN_FILES_PATH = "/home/james/tmp/ChemAZ_Corpus/withSents"
    TEST_FILES_PATH  = "/home/james/tmp/ChemAZ_Corpus/noSents"
    CLASSIFIER_FILE  = "/home/james/tmp/classifier.pickle"
    
    all_sents = []
    fullpaths = []
    for root, dirs, files in os.walk(TRAIN_FILES_PATH):
        
        fullpaths += [ os.path.join(root, file) for file in files 
                     if file.endswith(".xml")]

    print "Found %i files" % len(fullpaths)
    
    trainfiles = fullpaths[:(len(fullpaths) / 2)]
    testfiles  = fullpaths[(len(fullpaths)/2):]


    
    pool = multiprocessing.Pool(8)  
    filefeatures = pool.map(get_file_training_features, fullpaths)
    
    features =  reduce( lambda x,y: x+y, 
                        filefeatures)
    
    print "Training model on %i files (%i sentences) " % (len(trainfiles), len(features) )
    classifier = Classifier.train(features)
    
    with open(CLASSIFIER_FILE, 'wb') as f:
        cPickle.dump(classifier, f, )
            
    print "Testing on %i files" % len(testfiles)
    
    toklist = []
    for file in fullpaths:
        basename = os.path.basename(file)
        fileid = basename[:basename.find(".")]
        filename = os.path.join(TEST_FILES_PATH, fileid + ".xml")
        for paragraph in extract_plevel_text(filename):
            toklist += zip(paragraph, list(text_to_features(paragraph)))
        
    position = 1
    accumulator = []
    for token, feature in toklist:
        
        #feature['position'] = position
        position += 1
        
        if is_str(token):
            accumulator.append(token.strip())
        else:
            accumulator.append("<" + token.tag + ">")
        

        if classifier.classify(feature):
            position = 1
            print "<s>" + " ".join(accumulator) + "</s>"
            accumulator = []

    print classifier.show_most_informative_features()
    
    #print len(features)
            
    #for f in features:
    #    print f