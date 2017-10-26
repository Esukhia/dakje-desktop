

from typing import List, Set

from RDRPOSTagger import strTag, getPartOfSpeeches
from pytib import Segment

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

        self.RDRPath = 'Tibetan.RDR'
        self.DICTPath = 'Tibetan.DICT'
        self._words = []

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
            return self._words[index:]

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
            noSegBlocks =  [(0, textLen, 0)]

        else:
            index = 0
            wordIndex = 0
            start, end = None, None
            while True:
                if index == textLen or wordIndex == len(self._words):
                    break

                if index == self._words[wordIndex].end:
                    if index == self._words[wordIndex + 1].start:
                        # 同時也等於下一個字的開始
                        wordIndex += 1
                    else:
                        if not start:
                            start = index
                            wordIndex += 1
                elif index == self._words[wordIndex].start:
                    if start:
                        end = index
                        noSegBlocks.append((start, end, wordIndex))
                        start = None
                index += 1

        return noSegBlocks

    def reSegmentWord(self, curPos, prePos, text):
        # position 介於 start, end 之間(不包含)，用在 插入空白
        start, end, index = None, None, None
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
