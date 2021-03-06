'''
Created on 7 Mar 2012
http://nlp.stanford.edu/software/dependencies_manual.pdf
http://bulba.sdsu.edu/jeanette/thesis/PennTags.html

#TODO
-remove unigrams with frequency <=3
-remove verbs with freqency of 1
-remove gr triples with frequency <=3
-remove relationmap with frequency of 1

start the CandC soap server with
/nfs/research2/textmining/grabmuel/aho/coresc/candc/candc-min/bin/soap_server --models /nfs/research2/textmining/sapienta/software/softwares/candc-1.00/models --candc-pos /nfs/research2/textmining/sapienta/software/softwares/candc-1.00/models/pos_bio-1.00 --candc-pos-maxwords 900 --candc-parser /nfs/research2/textmining/sapienta/software/softwares/candc-1.00/models/parser --candc-super /nfs/research2/textmining/sapienta/software/softwares/candc-1.00/models/super_coresc/ --candc-parser-markedup /nfs/research2/textmining/sapienta/software/softwares/candc-1.00/models/parser/cats/markedup_new --candc-super-maxwords 900 --candc-parser-maxwords 900 --server localhost:9004 


@author: grabmuel
'''

from collections import Counter

from suds.client import Client
from .bnc import BncFilter
import unicodedata
import unittest
import logging
import pdb
import os
import re

import sapienta

bnc = BncFilter()

# figure out where the wsdl file is
wsdlPath = 'file:' + \
    os.path.join(os.path.dirname(__file__), "../../ccg_binding.wsdl")


logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)


class Features:
    interestingRelations = set(['dobj', 'iobj', 'ncsubj', 'obj2'])
    passiveRelation = 'passiveNcsubj'
    verbClassDefinition = {
        'class1': ['give', 'involve', 'provide', 'kcal', 'contain', 'carry', 'yield', 'stretch', 'represent', 'reflect', 'play', 'reach', 'include', 'allow', 'exhibit', 'combine', 'display', 'detail'],
        'class2': ['fit', 'extend', 'shift', 'attribute', 'compare', 'reduce', 'assign', 'relate', 'set', 'apply', 'bind', 'couple', 'add', 'limit'],
        'class3': ['fix', 'associate', 'excite', 'depend', 'charge', 'label', 'select', 'base', 'adsorb', 'mix'],
        'class4': ['vary', 'bond', 'quench', 'result', 'exist', 'change', 'arise', 'occur', 'increase', 'start', 'differ', 'consist', 'decrease', 'state', 'point'],
        'class5': ['calculate', 'employ', 'study', 'perform', 'identify', 'achieve', 'derive', 'monitor', 'introduce', 'discuss', 'detect', 'develop', 'determine', 'prepare', 'describe', 'examine', 'estimate', 'obtain', 'remove', 'investigate', 'evaluate', 'locate', 'measure', 'treat', 'compute', 'record'],
        'class6': ['illustrate', 'explain', 'suggest', 'predict', 'indicate', 'require', 'show', 'reveal', 'confirm', 'follow', 'demonstrate'],
        'class7': ['affect', 'enhance', 'improve', 'characterize', 'support', 'form', 'produce', 'isolate', 'separate', 'induce', 'modify', 'generate', 'control', 'cause', 'define'],
        'class8': ['interest', 'make', 'take', 'list', 'remain', 'lie', 'use', 'choose', 'need', 'present', 'become'],
        'class9': ['report', 'assume', 'note', 'observe', 'expect', 'consider', 'propose', 'find', 'see', 'conclude', 'know'],
        'class10': ['seem', 'accord', 'appear', 'correspond', 'lead', 'contribute']
    }

    verbToClass = {}
    for clas, verbs in verbClassDefinition.items():
        for verb in verbs:
            verbToClass[verb] = clas

    def __init__(self, relationTriples, tokens):
        self.relationTriples = relationTriples
        self.relationMap = self.createRelationMap(relationTriples)
        self.tokens = tokens

        self.unigrams, self.bigrams, self.trigrams = self.createNgrams(
            self.tokens)
        self.verbs, self.verbsPos = self.createVerbsVerbspos(tokens)
        self.verbClasses = self.createVerbClasses(self.verbs)
        self.passive = self.createPassiveFlag(relationTriples)

    def createNgrams(self, tokens):
        unigrams = [token.split('|')[1] for token in tokens if token != ""]
        unigrams = list(map(self.escapePunctuation, unigrams))
        #unigrams = [uni for uni in unigrams if not bnc.isStopWord(uni)]
        # TODO clean punctuation

        for i in range(0, len(unigrams)):

            # lower case all the things
            unigrams[i] = unigrams[i].lower()

            # filter out digits in favour of at symbols
            chars = [x if not x.isdigit() else '@@@' for x in unigrams[i]]
            unigrams[i] = "".join(chars)

            # shorten all floats to standard length
            unigrams[i] = re.sub(r'\@+\.\@+', "@@@.@@@", unigrams[i])

        bigrams = []
        for i in range(len(unigrams) - 1):
            bigrams.append(unigrams[i] + " " + unigrams[i + 1])

        trigrams = []
        for i in range(len(unigrams) - 2):
            trigram = (unigrams[i], unigrams[i + 1], unigrams[i+2])
            trigrams.append(" ".join(trigram))

        # filter out specific numbers and parenthesis in the unigrams, bigrams
        bigrams = map(self.escapePunctuation, bigrams)

        return unigrams, bigrams, trigrams

    def escapePunctuation(self, ngram):
        """Make sure that ngram punctuation makes sense"""

        if ngram == "":
            return ""

        brackets = "[{()}]"

        #logger.debug("Input: '%s'", ngram)

        words = ngram.split(" ")

        final_words = []

        # iterate through each word in the ngram
        for word in words:
            chars = list(word)

            if (len(chars) > 1) and (chars[-1] in ";,"):
                chars.pop(-1)

            for i, ch in enumerate(chars):
                if ch in brackets:
                    chars.pop(i)

            # now add word to "final words" list
            final_words.append("".join(chars))

        #logger.debug("output: '%s'", " ".join(final_words))
        # end for words and return words imploded together with spaces inbetween
        return " ".join(final_words)

    def createRelationMap(self, relationTriples):
        relMap = {}
        for relation, _, target in relationTriples:
            if not relation in relMap:
                relMap[relation] = []
            relMap[relation].append(target)
        return relMap

    def createVerbsVerbspos(self, tokens):
        verbs = []
        verbsPos = set()
        for token in tokens:
            splits = token.split('|')
            tag = splits[2]
            if tag.startswith('VB'):
                verbs.append(splits[1])
                verbsPos.add(tag)
        return verbs, verbsPos

    def createVerbClasses(self, verbs):
        verbClasses = []
        for verb in verbs:
            if verb in self.verbToClass:
                verbClass = self.verbToClass[verb]
                verbClasses.append(verbClass)
        return verbClasses

    def createPassiveFlag(self, relationTriples):
        containsPassive = False
        for relation, _, _ in relationTriples:
            if relation == self.passiveRelation:
                containsPassive = True
        return containsPassive

    def __str__(self):
        return '''
        relationTriples: %s
        relationMap: %s
        tokens: %s
        unigrams: %s
        bigrams: %s
        verbs: %s
        verbsPos: %s
        passive: %s
        ''' % (self.relationTriples, self.relationMap, self.tokens,
               self.unigrams, self.bigrams,
               self.verbs, self.verbsPos, self.passive)

    def __repr__(self):
        return str(self)


class SoapClient:

    def __init__(self):
        self.suds = Client(wsdlPath)
        if 'SAPIENTA_CANDC_SOAP_LOCATION' in os.environ:
            self.suds.options.location = os.environ['SAPIENTA_CANDC_SOAP_LOCATION']
        else:
            self.suds.options.location = "http://127.0.0.1:9004/"

        logger.info("Using C&C instance at %s", self.suds.options.location)

    def callSoap(self, s):
        # TODO ascii only input? caused by soap server?
        s = self.cleanseInput(s)

        #s = unicodedata.normalize('NFKD', s)
        # if type(s) is unicode:
        #     ascii = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
        # else:
        #     ascii = s

        s = s.encode("ascii","replace").decode()
        result = self.suds.service.parse_string(s, False)
        return result

    def cleanseInput(self, s):
        """Cleanse input sentence s"""

        if s == "":
            return u""

        # If this is a one-char sentence, just return here
        if len(s) == 1:
            return s

        # separate out punctuation , ; : ? is moved a space away from the words
        s = re.sub(r'(?<!(\s))(\,|\:|\?|\;)(?=(?:\s))',
                   lambda m: " " + (m.group(2) or ''), s)

        # move fullstop away from last word, i.e. end of sentence. -> end of sentence .
        if (s[-1] == ".") and (s[-2] != " "):
            s = s[:-1] + " ."

        words = s.split(" ")

        final_words = []
        for word in [word.strip() for word in words]:

            if len(word) < 1:
                continue

            if (word[0] in "[{(") and (len(word.split(word[0])) == 2):

                # if the word is surrounded by brackets, do (word) -> ( word )
                if re.match(r'^(\[)(.+?)(\])$|^(\{)(.+?)(\})$|^(\()(.+?)(\))$', word):
                    word = re.sub(
                        r'^(\[|\{|\()(.+?)(\]|\}|\))$', r'\1 \2 \3', word)
                # if word has weird brackets, separate i.e. (word}   ->  (word }
                elif re.match(r'^(\[|\{|\()(.+?)(\]|\}|\))$', word):
                    word = re.sub(r'^(.+?)(\]|\}|\))$', r'\1 \2', word)

                # if the word has no closing bracket move opening bracket (word -> ( word
                elif len(re.split(r'\]|\}|\)', word)) == 1:
                    word = word[0] + " " + word[1:]

            elif word[-1] in "]})":
                word = word[:-1] + " " + word[-1]

            final_words.append(word)

        return " ".join(final_words)

    def parseResult(self, result):
        relationTriples = []
        for line in result.splitlines():
            if line.startswith('('):
                splits = line.split(' ')
                relation = splits[0][1:]
                if relation in Features.interestingRelations:
                    middle = splits[1].split('_')[0]
                    target = splits[2].split('_')[0]
                    if line.endswith('obj)'):
                        relation = Features.passiveRelation
                    relationTriples.append((relation, middle, target))

        tokens = []
        for line in result.splitlines():
            if line.startswith('<c>'):
                tokens += line.split(' ')[1:]
        tokens = filter(lambda x: '|' in x, tokens)

        return Features(relationTriples, tokens)

    def getFeatures(self, sentence):
        result = self.callSoap(sentence)
        if not result:
            features = Features([], [])
        else:
            features = self.parseResult(result)
        return features


class TestCandC(unittest.TestCase):

    def setUp(self):
        self.client = SoapClient()

    def testCallSoap(self):
        result = self.client.callSoap(
            u'Pierre thinks that Mary persuaded Bill to eat the apple.')
        print(result)
        self.assertIn('(dobj persuaded_4 Bill_5)', result)
        #self.assertIn('<c> Pierre|pierre|NNP|I-NP|I-PER|N', result)
        self.assertIn('<c> Pierre|pierre|NN|I-NP|O|N/N', result)

    def testParseResult(self):
        result = self.client.callSoap(
            u'Pierre thinks that Mary persuaded Bill to improve the apple.')
        features = self.client.parseResult(result)
        self.assertIn(('dobj', 'persuaded', 'Bill'), features.relationTriples)
        self.assertIn('Bill', features.relationMap['ncsubj'])
        #self.assertIn('Pierre|pierre|NNP|I-NP|I-PER|N', features.tokens)
        self.assertIn('Pierre|pierre|NN|I-NP|O|N/N', features.tokens)
        self.assertIn('pierre', features.unigrams)
        self.assertIn(('pierre', 'think'), features.bigrams)
        self.assertIn(('pierre', 'think', 'Mary'), features.trigrams)
        #self.assertIn('think', features.verbs)
        self.assertIn('persuade', features.verbs)
        self.assertIn('class7', features.verbClasses)
        #self.assertIn('VBZ', features.verbsPos)
        self.assertIn('VB', features.verbsPos)

    def testPassive(self):
        result = self.client.callSoap(
            u'The burglar was arrested by the police.')
        features = self.client.parseResult(result)
        self.assertIn((Features.passiveRelation, 'arrested',
                       'burglar'), features.relationTriples)
        self.assertTrue(features.passive)


if __name__ == '__main__':
    unittest.main()
