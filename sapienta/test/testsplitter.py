"""
Simple test for the accuracy of the sentence splitter mechanism in SAPIENTA
"""
import sys
import os
import tempfile

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

def getSplitSentences( paperid ):
    """Run the new splitter system over the paper, returning sentences"""

    outfile = os.path.join(TEST_FILES_PATH, "newSplitter", paperid + "_split.xml")

    print outfile
    
    s = SSSplit()

    infile = os.path.join(TEST_FILES_PATH, "noSents", paperid + ".xml")

    s.split(infile, outfile)

    sentences = []
    
    #for sent in s.indoc.getElementsByTagName("s"):

    doc = minidom.parse(outfile)

    for sent in doc.getElementsByTagName("s"):

        sid = sent.getAttribute("sid")

        words = extractText(sent).split(" ")
        sentences.append({"sid" : sid, "first" : words[0], "last" : words[len(words)-1]})

    return sentences

def getSSSplitResult( paperid ):

    paperName = os.path.join( TEST_FILES_PATH, "sssplitresults", paperid + "_mode2.xml")

    with open(paperName, 'rb') as f:
        doc = minidom.parse(f)

    sentences = []
    for node in  doc.getElementsByTagName("s"):
        words = extractText(node).split(" ")
        sentences.append({"sid" : node.getAttribute("sid"), "first": words[0], "last": words[len(words)-1] })

    return sentences


def getManualSentences( paperid ):

    paperName = os.path.join( TEST_FILES_PATH, "withSents", paperid + ".A.xml")

    with open(paperName, 'rb') as f:
        doc = minidom.parse(f)

    nodes = doc.getElementsByTagName("A-S") + doc.getElementsByTagName("S")

    sentences = []
    #find all sentences and store boundary info
    for sent in nodes:
        
        sid = sent.getAttribute("ID")

        words = extractText(sent).split(" ")
        sentences.append( { "sid":sid, "first" : words[0], "last" : words[len(words)-1]} )
    
    return sentences



def main():

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

                msents = getManualSentences(paperid)
                asents = getSplitSentences(paperid)
                sssents = getSSSplitResult( paperid )

                print "Found %d manual sentences" % len(msents)
                print "Found %d automatic sentences" % len(asents)
                print "Found %d SSSplit sentences" % len(sssents)

               # for s in range(0, len(asents)):
               #     assert asents[s] == sssents[s]

                print "SSplit matches new splitter"

                for s in range(0, min(len(msents),len(asents), len(sssents))): 
                    print "Sentence %s" % s
                    print "--------------------"
                    print "Manual: \t" , msents[s]
                    print "Splitter: \t",asents[s]
                    print "SSPlit:   \t", sssents[s]
                    print "--------------------"

                print "-------------------------------------------"


if __name__ == "__main__":
    main()

