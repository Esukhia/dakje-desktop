
import os
import misc

from typing import List, Set

from RDRPOSTagger import strTag, getPartOfSpeeches
from pytib import Segment

class Word:
    def __init__(self, content):
        self.content = content
        self.partOfSpeech = None
        self.level = None


class WordManager:
    def __init__(self):
        self.RDRPath = 'Tibetan.RDR'
        self.DICTPath = 'Tibetan.DICT'

    def getPartOfSpeeches(self) -> Set[str]:
        return getPartOfSpeeches(self.DICTPath)

    def segment(self, sentence: str) -> List[Word]:
        return [Word(s) for s in Segment().segment(sentence).split()]

    def tag(self, words: List[Word]) -> List[Word]:
        taggedWords = []
        for wordStr in strTag(' '.join([w.content for w in words]),
                              self.RDRPath, self.DICTPath).split():
            content = wordStr.split('/')[0]
            partOfSpeech = wordStr.split('/')[1]
            newWord = Word(content)
            newWord.partOfSpeech = partOfSpeech
            taggedWords.append(newWord)

        for index, word in enumerate(words):
            word.partOfSpeech = taggedWords[index].partOfSpeech

        assert len(words) == len(taggedWords)

