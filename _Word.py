

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
            words = []
            for s in Segment().segment(sentence, unknown=0, reinsert_aa=False, space_at_punct=True, distinguish_ra_sa=True, affix_particles=True).split(' '):
                if s:
                    # 1.
                    if s == '\n':
                        words.append(Word(s))
                    # 2. the location of \n in s in unknown
                    elif '\n' in s:
                        i = 0
                        sub_word = ''
                        while i < len(s):
                            if s[i] != '\n':
                                sub_word += s[i]
                            else:
                                if sub_word != '':
                                    words.append(Word(sub_word.replace('ᛰ', '')))
                                    sub_word = ''
                                words.append(Word('\n'))
                            i += 1
                    # 3.
                    else:
                        words.append(Word(s.replace('ᛰ', '')))  # char used to mark affixed particles
            return words

    def tag(self, words: List[Word]) -> None:
        tags = []

        batchWords = []
        for word in words:
            if word.content == '\n':
                for wordStr in strTag(' '.join([w.content for w in batchWords]),
                                      self.RDRPath, self.DICTPath).split(' '):
                    partOfSpeech = wordStr.split('ᚽ')
                    if len(partOfSpeech) > 1:  # is split by '/'
                        tags.append(partOfSpeech[1])
                tags.append('NOUN')
                batchWords = []
            else:
                batchWords.append(word)

        if batchWords:
            for wordStr in strTag(' '.join([w.content for w in batchWords]),
                                  self.RDRPath, self.DICTPath).split(' '):
                partOfSpeech = wordStr.split('ᚽ')[1]
                tags.append(partOfSpeech)

        for index, word in enumerate(words):
            word.partOfSpeech = tags[index]

        assert len(words) == len(tags)

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
