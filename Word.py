
import os
import misc

from typing import List, Set

from RDRPOSTagger import strTag, getPartOfSpeeches
from pytib import Segment

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont


class Word:
    def __init__(self, content):
        self.content = content
        self.partOfSpeech = None
        self.tagIsOn = False
        self.level = 0
        self.start = 0

    @property
    def __len__(self):
        return len(self.content)

    @property
    def end(self):
        return self.start + len(self.content) - 1

    @property
    def partOfSpeechStart(self):
        return self.end + 1

    @property
    def partOfSpeechEnd(self):
        return self.partOfSpeechStart + self.partOfSpeechLen - 1

    @property
    def partOfSpeechLen(self):
        return len(self.partOfSpeech) + 1 # plus one for '/'


class WordManager:
    def __init__(self):
        self.RDRPath = 'Tibetan.RDR'
        self.DICTPath = 'Tibetan.DICT'
        self.wordsLevelDict = {}

        for level in range(1, 4):
            with open('files/Lists/General/{0}/General_Level_{0}'.format(
                    level), encoding='utf-8') as f:
                for line in f.readlines():
                    word = line.rstrip('\n')
                    # add a tsek where missing
                    if not word.endswith('་'):
                        word += '་'
                    self.wordsLevelDict[word] = level

    def getPartOfSpeeches(self) -> Set[str]:
        return getPartOfSpeeches(self.DICTPath)

    def segment(self, sentence: str) -> List[Word]:
        if sentence == '':
            return []
        else:
            return [Word(s.replace('#', ''))
                    for s in Segment().segment(sentence, reinsert_aa=True).split()]

    def tag(self, words: List[Word]) -> None:
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

    def checkLevel(self, words: List[Word]) -> None:
        for word in words:
            word.level = self.wordsLevelDict.get(word.content, 0)
