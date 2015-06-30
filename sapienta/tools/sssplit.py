#import xml.etree.cElementTree as ET
import sys
import re
import lxml.etree as ET

highLevelContainerElements = ["DIV", "sec"]
pLevelContainerElements = ["P", "region"]
abstractLevelContainerElements = ["abstract", "ABSTRACT"]
referenceElements = ["REF"]
commonAbbreviations = ['Fig', 'Ltd', 'St', 'al']

class SSSplit:


    def normalize_sents(self):

        for i,s in enumerate(self.root.iter("s")):

            #set sentence ID
            s.set("sid", str(i+1))

    def load_authors(self):
        """Parse authors from citations and add to do not split list"""

        self.authors = []

        for el in self.root.iter('AUTHOR'):
            self.authors.append(" ".join(list(el.itertext())))


    def split(self, filename, outname=None):
        tree = ET.parse(filename)
        self.root = tree.getroot()

        #load list of referenced authors for sentence splitting purposes
        self.load_authors()

        #first find and split abstract(s) (special case p-level container)
        for container in abstractLevelContainerElements:
            for el in self.root.findall(container):
                self.split_plevel_container(el)

        #now we handle remaining high level containers such as <DIV> or <sec>
        for container in highLevelContainerElements:
            for el in self.root.iter(container):
                self.split_high_level_container(el)

        #assign sentence ids
        self.normalize_sents()

        if outname != None:
            tree.write(outname, pretty_print=True)
        else:
            return ET.tostring(self.root, pretty_print=True)

    def split_high_level_container(self, containerEl):
        """A high level container is a section or similar
        
        High-level containers are container elements that contain p-level
        containers and do not have text or sentences as direct descendents.
        
        Examples of high level containers are <DIV> in SciXML and <section> 
        in DoCo XML"""

        for containerType in pLevelContainerElements:
            for el in set(containerEl.findall(containerType)):
                self.split_plevel_container(el)
        

    def split_plevel_container(self, containerEl):
        """A p-level container is a paragraph or similar
        
        P-level containers are containers that can contain text nodes as direct
        descendents i.e. <P> in SCIXML or a <region> in DoCoXML.

        This method splits sentences contained in P level containers taking into
        account the presence of sub-elements such as <xref> tyoes
        """

        #get a list of all child elements in containerNode to analyse
        siblings = list(containerEl)

        #if the container element has text insert in front of other siblings
        if containerEl.text != None:
            siblings = [ containerEl.text] + siblings

        self.splitSentences(siblings, containerEl)

    def splitSentences(self, nodeList, containerEl):
        """This xml-aware method builds sentence lists using nodes"""

        #new node list is the list of <s> elements to be created
        self.newNodeList = []
        #newsentence is the accumulator for sentence elements and strings
        self.newSentence = []

        #first we walk through all nodes inside the container
        while len(nodeList) > 0:
            
            el = nodeList.pop(0)

            #if the node is a string (or unicode)
            #run text splitting routine on it
            if isinstance(el,str) or isinstance(el,unicode):
                self.splitTextBlock(el)

            # if node is an element, append it to the current sentence
            else:
            
                #if the node is a <REF> and this is a new sentence, chances are
                #it should be appended to the previous sentence
                # e.g. "this is the end of my sentence. [1]" 
                if len(self.newSentence) < 1 and el.tag in referenceElements:

                    textProc = None
                    if el.tail != None:
                        textProc = el.tail
                        el.tail = None

                    self.newNodeList[-1].append(el)
                    
                    if textProc != None:
                        self.splitTextBlock(textProc)
                else:
                    self.newSentence.append(el)
                    if el.tail != None:
                        self.splitTextBlock(el.tail)
                        #now remove the 'old' tail since the new one will be appended
                        el.tail = None

        # when we run out of child nodes for p-level container we know
        # we're at the end of the current sentence 
        # (sentences don't cross <p></p> boundaries)
        self.endCurrentSentence()

#         for i,sent in enumerate(self.newNodeList[:]):
# 
#             if isinstance(sent[0],str) or isinstance(sent[0],unicode):
#                 self.newNodeList[i-1].extend(sent)
#                 self.newNodeList.remove(sent)

        # now we can be confident that we're finished with this container
        # so we can generate final xml form
        self.endPLevelContainer(containerEl)

    def splitTextBlock(self, txt, beforeNode=None):
        txt = txt.strip()
        pattern = re.compile('(\.|\?|\!)(?=\s*[A-Z0-9$])|\.$')

        m = pattern.search(txt)
        last = 0


        while m != None:

            # assume that the punctuation matched is the end of the sentence
            # (until otherwise proven)
            endOfSent = True

            #get last word before full stop (if not full stop we don't care)
            lastmatch = re.search("[\(\[]?(\S+)\.$", txt[last:m.end()])
            
            if lastmatch != None:
                lastword = lastmatch.group(1)
            else:
                lastword = None
            

            #if the last word is a common abbreviation, skip end of sentence
            if lastword != None and lastword in commonAbbreviations:
                endOfSent = False
                
            #if the last word is a single letter then it is usually an initial
            if lastword != None and len(lastword) == 1 and lastword.isupper():
                endOfSent = False
            
            if txt[last:m.end()] != '':
                self.newSentence.append(txt[last:m.end()])
            
            last = m.end()


            #if the dot matches the end of a common abbreviation, skip end of sentence

            #if we match digits around a dot then its probably a number so skip
            if re.match("[0-9]\.[0-9]", txt[m.start()-1:m.end()+1]):
                endOfSent = False


            #check if we should be ending the sentence this time around the loop
            if endOfSent:
                self.endCurrentSentence()

            m = pattern.search(txt, last)

        #the remnants of the string are the beginning of the next sentence
        if txt[last:] != '':
            self.newSentence.append(txt[last:])

        # note: we don't end sentence by default at this point because this could
        # just be the end of the text block and the start of a reference or formatting


    def endCurrentSentence(self):
        """Ends the current sentence being accumulated
        """
        if self.newSentence != []:
            #print self.newSentence
            self.newNodeList.append(self.newSentence)
            self.newSentence = []

    def endPLevelContainer(self, pContainer):
        """Process updates/splits in the current p-level container"""
        #prune all children of p container
        pContainer.text = None
        for el in pContainer:
            pContainer.remove(el)

        #generate sentences and append to container
        prevSent = None
        for sent in self.newNodeList:
            prevSent = self.generateSentence(sent,pContainer, prevSent)
            


    def generateSentence(self, sent, parent, prevSent):
        """Takes a list of strings and elements and turn into an <s> element
        
        Using the element tree subelement factory, create a sentence from
        a list of str and legal descendents (i.e. xref, ref)
        """
        
        sentEl = ET.SubElement(parent, "s")

        prevEl = None
        refOnly = True

        for item in sent:
            #are we dealing with text (string or unicode)
            if isinstance(item,str) or isinstance(item,unicode):
                #refOnly is no longer true because we found text
                refOnly = False
                #if prev item is not set this is the first text node in the sentence
                if prevEl == None:
                    if sentEl.text != None:
                        sentEl.text += item
                    else:
                        sentEl.text = item
                #if prev item is set, this will be tacked on as the 'tail'
                else:
                    if prevEl.tail != None:
                        prevEl.tail += item
                    else:
                        prevEl.tail = item

            #else we're dealing with an element not text
            else:
                prevEl = item
                sentEl.append(item)

        if refOnly:
            parent.remove(sentEl)

            for item in sent:
                prevSent.append(item)

            return prevSent
        else:
            return sentEl

    


if __name__ == "__main__":
    splitter = SSSplit()
    print splitter.split("b103844n_nosents.xml")
    
