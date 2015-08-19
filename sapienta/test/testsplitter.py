"""
Simple test for the accuracy of the sentence splitter mechanism in SAPIENTA
"""
import sys
import os
import tempfile
import cPickle

from xml.dom import minidom

#from sapienta.tools.split import SentenceSplitter
from sapienta.tools.sssplit import SSSplit

TEST_FILES_PATH = "/home/james/tmp/ChemAZ_Corpus/"

def extractText( node ):
    """Recurse into dom nodes and extract any text in TEXT_NODE constructs"""

   
    text = ""
    
    for child in node.childNodes:

        if child.nodeType == node.ELEMENT_NODE:
            text += extractText(child)
        elif child.nodeType == node.TEXT_NODE:
            text += child.wholeText

    return text.strip()

def getSplitSentences( paperid, classifier ):
    """Run the new splitter system over the paper, returning sentences"""

    outfile = os.path.join(TEST_FILES_PATH, "newSplitter", paperid + "_split.xml")

    print outfile
    
    s = SSSplit()
    s.classifier = classifier

    infile = os.path.join(TEST_FILES_PATH, "noSents", paperid + ".xml")

    s.split(infile, outfile)

    doc = minidom.parse(outfile)

    return sentencesFromNodes(doc.getElementsByTagName("s"), "sid")

def getSSSplitResult( paperid ):

    paperName = os.path.join( TEST_FILES_PATH, "sssplitresults", paperid + "_mode2.xml")

    with open(paperName, 'rb') as f:
        doc = minidom.parse(f)

    return sentencesFromNodes(doc.getElementsByTagName("s"), "sid")

def sentencesFromNodes(nodeList, idAttribute):
    
    sentences = []
    words = []
    
    for sent in nodeList:
        sid = sent.getAttribute(idAttribute)
        sentWords = [ w.strip() for w in extractText(sent).strip().split(" ") if w.strip() != '' ]
        firstWord = len(words)
        words.extend(sentWords)
        sentences.append( { "sid":sid, "first" : firstWord, "last" : firstWord + len(sentWords) - 1  } )
        
    return sentences, words

def getManualSentences( paperid ):

    paperName = os.path.join( TEST_FILES_PATH, "withSents", paperid + ".A.xml")

    with open(paperName, 'rb') as f:
        doc = minidom.parse(f)

    nodes = doc.getElementsByTagName("A-S") + doc.getElementsByTagName("S")

    return sentencesFromNodes(nodes, "ID")

def compareSents(sentList1, sentList2):
    maxSents = max(len(sentList1),len(sentList2))
    minSents = min(len(sentList1),len(sentList2))
    matchingSents = 0
    
    for s in range(0, minSents):
        if ((sentList1[s]['first'] == sentList2[s]['first']) and 
            (sentList1[s]['last'] == sentList2[s]['last'])):
            
            matchingSents += 1
            
    return matchingSents, maxSents, (matchingSents*100/maxSents)



def main():
    
    matchedManual = 0
    matchedSSSPlit = 0
    
    totalSentsMatchedSSSplit = 0
    totalSentsMatchedManual = 0
    totalSents = 0
    papers = 0
    
    CLASSIFIER_FILE  = "/home/james/tmp/classifier.pickle"
        
    with open(CLASSIFIER_FILE) as f:
        classifier = cPickle.load(f)

    unsplit = os.path.join(TEST_FILES_PATH, "noSents")
    for root, dirs, files in os.walk(unsplit):

        for file in files:

            if len(sys.argv) > 1 and sys.argv[1] not in file:
                continue

            if file.endswith(".xml"):
                name,ext = os.path.splitext(file)
                paperid = name

                print "--------------------------------------------"
                print "In paper: %s" % paperid
                
                offset = 0
                matchesManual  = True
                matchesSSSplit = True

                msents,mwords = getManualSentences(paperid)
                asents,awords = getSplitSentences(paperid, classifier)
                sssents,sswords = getSSSplitResult( paperid )

                print "Found %d manual sentences" % len(msents)
                print "Found %d automatic sentences" % len(asents)
                print "Found %d SSSplit sentences" % len(sssents)

                print "SSplit matches new splitter"

                for s in range(0, min(len(msents),len(asents), len(sssents))): 
                    print "Sentence %s" % s
                    print "--------------------"
                    print "Manual: \t" , " ".join(mwords[msents[s]['first']:msents[s]['last']+1])
                    print "Splitter: \t"," ".join(awords[asents[s]['first']:asents[s]['last']+1])
                    #print "SSPlit:   \t", sssents[s]
                    print "--------------------"
                    
                    print "asent_start %i, msent_start: %i" % ( asents[s]['first'], msents[s]['first'] )
                    print "msent_last %i, msent_last: %i" % ( asents[s]['last'], msents[s]['last'])
                    
                    try:
                        assert msents[s]['first'] == asents[s]['first']
                        assert msents[s]['last'] == asents[s]['last']
                        totalSentsMatchedManual += 1
                    except:
                        matchesManual = False
                        offset += msents[s]['last'] - asents[s]['last']
                        print offset
                        
                                            
                    try:
                        assert sssents[s]['first'] == asents[s]['first']
                        assert sssents[s]['last'] == asents[s]['last']
                        totalSentsMatchedSSSplit += 1
                    except:
                        matchesSSSplit = False
                        
                    totalSents += 1
                        

                print "-------------------------------------------"
                
                papers += 1
                
                if matchesManual:
                    matchedManual += 1
                    
                if matchesSSSplit:
                    matchedSSSPlit += 1
                    
    print "----------------------------------"
    
    print "%i / %i papers matched manual split" % (matchedManual, papers )
    print "%i / %i papers matched old sssplit implementation" % (matchedSSSPlit, papers)

    print "-----------------------------"
    print "Total sentences that matched (SSSplit) %i/%i (%i%%)" %(totalSentsMatchedSSSplit, totalSents, totalSentsMatchedSSSplit*100/totalSents)
    print "Total sentences that matched (Manual) %i/%i (%i%%)" % (totalSentsMatchedManual, totalSents, totalSentsMatchedManual*100/totalSents)
if __name__ == "__main__":
    main()

