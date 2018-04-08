# -*- coding: utf-8 -*-

import os
import sys
os.chdir("../")
sys.setrecursionlimit(100000)
sys.path.append(os.path.abspath(""))
# os.chdir("../")


from multiprocessing import Pool
from InitialTagger.InitialTagger import initializeCorpus, initializeSentence
from SCRDRlearner.Object import FWObject
from SCRDRlearner.SCRDRTree import SCRDRTree
from SCRDRlearner.SCRDRTreeLearner import SCRDRTreeLearner
from Utility.Config import NUMBER_OF_PROCESSES, THRESHOLD
from Utility.Utils import getWordTag, getRawText, readDictionary
from Utility.LexiconCreator import createLexicon

def unwrap_self_RDRPOSTagger(arg, **kwarg):
    return RDRPOSTagger.tagRawSentence(*arg, **kwarg)

class RDRPOSTagger(SCRDRTree):
    """
    RDRPOSTagger for a particular language
    """
    def __init__(self):
        self.root = None

    def tagRawSentence(self, DICT, rawLine):
        line = initializeSentence(DICT, rawLine)
        sen = []
        wordTags = line.split()
        for i in range(len(wordTags)):
            fwObject = FWObject.getFWObject(wordTags, i)
            word, tag = getWordTag(wordTags[i])
            node = self.findFiredNode(fwObject)
            if node.depth > 0:
                sen.append(word + "/" + node.conclusion)
            else:# Fired at root, return initialized tag
                sen.append(word + "/" + tag)
        return " ".join(sen)

    def tagRawCorpus(self, DICT, rawCorpusPath):
        lines = open(rawCorpusPath, "r").readlines()
        #Change the value of NUMBER_OF_PROCESSES to obtain faster tagging process!
        pool = Pool(processes = NUMBER_OF_PROCESSES)
        taggedLines = pool.map(unwrap_self_RDRPOSTagger, zip([self] * len(lines), [DICT] * len(lines), lines))
        outW = open(rawCorpusPath + ".TAGGED", "w")
        for line in taggedLines:
            outW.write(line + "\n")
        outW.close()
        print (("\nOutput file:", rawCorpusPath + ".TAGGED"))

def printHelp():
    print (("\n===== Usage ====="  ))
    print ('\n#1: To train RDRPOSTagger on a gold standard training corpus:')
    print ('\npython RDRPOSTagger.py train PATH-TO-GOLD-STANDARD-TRAINING-CORPUS')
    print ('\nExample: python RDRPOSTagger.py train ../data/goldTrain')
    print ('\n#2: To use the trained model for POS tagging on a raw text corpus:')
    print ('\npython RDRPOSTagger.py tag PATH-TO-TRAINED-MODEL PATH-TO-LEXICON PATH-TO-RAW-TEXT-CORPUS')
    print ('\nExample: python RDRPOSTagger.py tag ../data/goldTrain.RDR ../data/goldTrain.DICT ../data/rawTest')
    print ('\n#3: Find the full usage at http://rdrpostagger.sourceforge.net !')

def run(args = sys.argv[1:]):
    if (len(args) == 0):
        printHelp()
    elif args[0].lower() == "train":
        try:
            lexicon_path = '.' + args[1]
            goldTrain_path = os.path.join('RDRPOSTagger', args[1])

            print("\n====== Start ======"          )
            print("\nGenerate from the gold standard training corpus a lexicon", args[1] + ".DICT")
            createLexicon(lexicon_path, 'full')
            createLexicon(lexicon_path, 'short')
            print("\nExtract from the gold standard training corpus a raw text corpus", args[1] + ".RAW")
            getRawText(goldTrain_path, goldTrain_path + ".RAW")
            print("\nPerform initially POS tagging on the raw text corpus, to generate", args[1] + ".INIT")
            DICT = readDictionary(goldTrain_path + ".sDict")
            initializeCorpus(DICT, goldTrain_path + ".RAW", goldTrain_path + ".INIT")
            print('\nLearn a tree model of rules for POS tagging from %s and %s' % (args[1], args[1] + ".INIT"))
            rdrTree = SCRDRTreeLearner(THRESHOLD[0], THRESHOLD[1])
            rdrTree.learnRDRTree(goldTrain_path + ".INIT", goldTrain_path)
            print ("\nWrite the learned tree model to file ", args[1] + ".RDR")
            rdrTree.writeToFile(goldTrain_path + ".RDR")
            print ('\nDone!')
            os.remove(goldTrain_path + ".INIT")
            os.remove(goldTrain_path + ".RAW")
            os.remove(goldTrain_path + ".sDict")
        except Exception as e:
            print ("\nERROR ==> ", e)
            printHelp()
            raise e
    elif args[0].lower() == "tag":
        try:
            rdr_path = os.path.join('RDRPOSTagger', args[1])
            dict_path = os.path.join('RDRPOSTagger', args[2])
            corpus_path = os.path.join('RDRPOSTagger', args[3])

            r = RDRPOSTagger()
            print ("\n=> Read a POS tagging model from", args[1])
            r.constructSCRDRtreeFromRDRfile(rdr_path)
            print ("\n=> Read a lexicon from", args[2])
            DICT = readDictionary(dict_path)
            print ("\n=> Perform POS tagging on", args[3])
            r.tagRawCorpus(DICT, corpus_path)
        except:
            print ("\nERROR ==> ")
            printHelp()
    else:
        printHelp()

if __name__ == "__main__":
    run()
    pass