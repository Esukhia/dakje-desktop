import os

from typing import Set
from .pSCRDRtagger.RDRPOSTagger import RDRPOSTagger
from .Utility.Utils import readDictionary

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POS_DIR = os.path.join(BASE_DIR, 'Models', 'POS')

def strTag(rawSentence, RDRPath, DICTPath):
    r = RDRPOSTagger()
    # Load the POS tagging model for French
    r.constructSCRDRtreeFromRDRfile(os.path.join(POS_DIR, RDRPath))
    # Load the lexicon for French
    DICT = readDictionary(os.path.join(POS_DIR, DICTPath))
    # Tag a tokenized/word-segmented sentence
    return r.tagRawSentence(DICT, rawSentence)


def getPartOfSpeeches(DICTPath) -> Set[str]:
    partOfSpeeches = set()
    with open(os.path.join(POS_DIR, DICTPath), encoding='utf-8') as f:
        for line in f.readlines():
            partOfSpeeches.add(line.split()[-1])
    return partOfSpeeches
