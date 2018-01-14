# -*- coding: utf-8 -*-
from typing import List, Set

from RDRPOSTagger import Tagger, models
from pytib import Segment
from NLPtokenizer import Tokenizer
from NLPpipeline import Pipeline

class Word:
    def __init__(self, content):
        self.content = content
        self.partOfSpeech = None
        self.tagIsOn = False
        self.level = 0
        self.start = 0
        self.length = len(self.content)

    @property
    def end(self):
        return self.start + len(self.content)

    @property
    def partOfSpeechEnd(self):
        return self.end + self.partOfSpeechLen

    @property
    def partOfSpeechLen(self):
        return len(self.partOfSpeech) + 1 # plus one for '/'


class WordManager:
    def __init__(self, parent):
        self.parent = parent
        self.lang = "bo"
        self.mode = "default"
        self.tagger = None
        self.tokenizer = None
        self._words = []

    def getPartOfSpeeches(self) -> Set[str]:
        partOfSpeeches = set()
        with open(models['{}_{}'.format(self.lang, self.mode)][1],
                  encoding='utf-8') as f:
            for line in f.readlines():
                partOfSpeeches.add(line.split()[-1])
        return partOfSpeeches

    def NLPtokenize(self, sentence: str) -> List[Word]:
        if not self.tokenizer:
            self.tokenizer = Segment()  # only instanciate when required
            self.tokenizer.include_user_vocab()
        return [Word(token) for token in Tokenizer(self.tokenizer).process(sentence)]

    def NLPpipeline(self, words: List[Word]) -> None:
        if not self.tagger or self.lang != self.tagger.language or self.mode != self.tagger.mode:
            self.tagger = Tagger(language=self.lang, mode=self.mode)  # only instanciate when required
        return Pipeline(self.tagger, words).applyPipeline()

    def getWords(self, start=None, end=None):
        if not start and not end:
            return self._words

        elif start and not end:
            # 大於等於 start
            index = None
            for i, word in enumerate(self._words):
                if word.start >= start:
                    index = i
                    break

            if not index:
                return []
            else:
                return self._words[index:]

        elif start is not None and end is not None:
            # 大於等於 start 小於等於 end
            words = []
            for i, word in enumerate(self._words):
                if word.start >= start:
                    words.append(word)
                if word.end >= end:
                    break
            return words

    def getPartOfSpeechWord(self, position):
        # position 介於 start, end 之間(不包含)，用在 changeTag
        for i, word in enumerate(self._words):
            if word.start < position < word.partOfSpeechEnd:
                return word

    def getWord(self, position):
        # position 介於 start, end 之間(不包含)，用在 changeTag
        for i, word in enumerate(self._words):
            if word.start < position < word.end:
                return word

    def removeWord(self, position):
        # position 介於 start, end 之間(不包含)，用在 插入字元在字中間
        for i, word in enumerate(self._words):
            if word.start < position < word.end:
                self._words.pop(i)
                return

    def removeWords(self, start, end):
        # start 剛好 < 第一個字的 end
        # end 剛好 > 最後一個字的 start
        if not self._words:
            return

        i = 0
        deleted = False
        deletedIndex = []
        while True:
            if start in range(self._words[i].start, self._words[i].end):
                deleted = True
            if deleted:
                deletedIndex.append(i)
            if end in range(self._words[i].start + 1, self._words[i].end + 1):
                deleted = False
            i += 1
            if i == len(self._words):
                break

        for i in reversed(deletedIndex):
            self._words.pop(i)

    def setWords(self, words):
        self._words = words

    def popWord(self, index):
        self._words.pop(index)

    def insertWordsByIndex(self, wordTuples):
        # [(Word('abc'), 3), ...] or
        # [(Word('abc'), 3),
        #  ([Word('abc'), Word('def')], 4)...]
        for wordTuple in wordTuples:
            self._words[wordTuple[1]: wordTuple[1]] = wordTuple[0]

    def getNoSegBlocks(self, textLen):  # return [(start, end, index), ...]
        noSegBlocks = []

        if not self._words:
            noSegBlocks = [(0, textLen, 0)]

        else:
            for i, word in enumerate(self._words):
                if i == len(self._words) - 1:
                    if not self._words[i].end == textLen:
                        noSegBlocks.append(
                            (self._words[i].end, textLen, i + 1))
                else:
                    if not self._words[i].end == self._words[i + 1]:
                        noSegBlocks.append(
                            (self._words[i].end,
                             self._words[i + 1].start, i + 1))

        return noSegBlocks

    def reSegmentWord(self, curPos, prePos, text):
        # position 介於 start, end 之間(不包含)，用在 插入空白
        for i, word in enumerate(self._words):
            if word.start == curPos and curPos < prePos:
                start, end, index = self._words[i - 1].start, word.end + 1, i - 1
                self._words.pop(i)
                self._words.pop(i - 1)
                break

            if word.start < prePos < word.end:
                start, end, index = word.start, word.end + 1, i
                self._words.pop(index)
                break
        else:
            return

        newWordStrings = text[start: end].split()
        newWords = [Word(s) for s in newWordStrings]
        self.tag(newWords)
        self.insertWordsByIndex([(newWords, index)])
