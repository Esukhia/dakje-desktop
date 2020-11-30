'''

'''

import os
import time
import botok
from pathlib import Path
# from PyQt5.QtCore import QThread, pyqtSignal

from storage.models import Rule
from storage.models import Token as TokenModel
from .ViewManager import ViewManager
from . import Matchers
from web.settings import BASE_DIR
from web.settings import FILES_DIR
from web.settings import createLogger
from web.settings import TEST_BY_ENG

logger = createLogger(__name__, "Tokens.txt")

from horology import timed
from diff_match_patch import diff

class TokenList(list):

    def setTokensStartAndEnd(self, tokensStart):
        for i, token in enumerate(self[tokensStart:]):
            lenOfEachTokenText = len(token.text)
            if i == 0: # 更改處的開始
                if tokensStart == 0: # 所有文字的最開始
                    token.start = 0
                else: # 上一個 end
                    token.start = self[tokensStart - 1].end
            else:
                token.start = self[i + tokensStart - 1].end
            token.end = token.start + lenOfEachTokenText

    def __init__(self, tokens=[]):
        super().__init__(tokens)
        if tokens:
            self.setTokensStartAndEnd(0)

    def __delitem__(self, key):
        super().__delitem__(key)
        self.setTokensStartAndEnd(key - 1)

    def remove(self, value):
        key = self.index(value)
        super().remove(value)
        self.setTokensStartAndEnd(key - 1)

    def __getitem__(self, key):
#         print('get')
        return super().__getitem__(key)

    def __setitem__(self, key, val):
#         print('set')
        if isinstance(key, slice):
            start, stop, step = key.indices(len(self))
            tokensStart = start
        else:
            tokensStart = key

        super().__setitem__(key, val)
        self.setTokensStartAndEnd(tokensStart)

    def extend(self, list):
        tokensLengthBeforeExtend = len(self)
        super().extend(list)
        self.setTokensStartAndEnd(tokensLengthBeforeExtend)

    def insert(self, key, val):
        super().insert(key, val[0])
        self.setTokensStartAndEnd(key)

    def append(self, val):
        self.insert(len(self), val)

    def pop(self, key):
        super().pop(key)
        self.setTokensStartAndEnd(key - 1)

    def count(self, value):
        raise RuntimeError('TokenList can not use the method of count.')

    def reverse(self):
        raise RuntimeError('TokenList can not use the method of reverse.')

    def sort(self, key=None, reverse=False):
        raise RuntimeError('TokenList can not use the method of sort.')

class Token:
    def __init__(self, token, id=None):
        """
        Class building token objects
        (pybo token attributes + custom attributes)
        IMPORTANT: .text_unaffixed should be used for lookups
        .text might include extra tseks
            :param self:
            :param token:
            :param id=None:
        """
        # copy all token attributes from pybo tokens
        self.text = token.text
        self.text_cleaned = token.text_cleaned
        self.text_unaffixed = token.text_unaffixed
        self.lemma = token.lemma
        self.pos = token.pos
        self.start = token.start        # index from the source string
        self.type = token.chunk_type
        # self.sense = token.sense      # no sense in pybo
        self.level = None
        self.sense = None

        self.id = id  # have no id before save to database

#         self.blockIndex = None
        self.end = self.start + len(self.text)
        self.string = None

    # @timed(unit='ms')
    def applyTokenModel(self, tokenModel):
        # add attributes from the DB
        self.pos = tokenModel.pos if tokenModel.pos else self.pos
        self.lemma = tokenModel.lemma if tokenModel.lemma else self.lemma
        self.level = tokenModel.level if tokenModel.level else self.level
        self.sense = tokenModel.sense if tokenModel.sense else self.sense

    @property
    def length(self):
        return self.end - self.start

    @property
    def textWithoutTsek(self):
        return (self.text_unaffixed[:-1] if self.text_unaffixed.endswith('་')
                                         else self.text_unaffixed)

class TokenManager:
    # This class runs botok, and gives him custom lists

    LANG_PACK_DIR = os.path.join(FILES_DIR, 'general')
    if not os.path.exists(LANG_PACK_DIR):
        os.makedirs(LANG_PACK_DIR)

    TRIE_BUILD_DIR = os.path.join(LANG_PACK_DIR, 'dictionary')
    if not os.path.exists(TRIE_BUILD_DIR):
        os.makedirs(TRIE_BUILD_DIR)

    TRIE_MODIF_DIR = os.path.join(LANG_PACK_DIR, 'adjustments')
    if not os.path.exists(TRIE_MODIF_DIR):
        os.makedirs(TRIE_MODIF_DIR)

    TRIE_ADD_DIR = os.path.join(TRIE_MODIF_DIR, 'remove')
    if not os.path.exists(TRIE_ADD_DIR):
        os.makedirs(TRIE_ADD_DIR)

    TRIE_DEL_DIR = os.path.join(TRIE_MODIF_DIR, 'words')
    # print(TRIE_DEL_DIR)
    if not os.path.exists(TRIE_DEL_DIR):
        os.makedirs(TRIE_DEL_DIR)

    TRIE_ADD_TEMP_FILE = os.path.join(TRIE_ADD_DIR, 'TrieAddTempFile.txt')
    TRIE_DEL_TEMP_FILE = os.path.join(TRIE_DEL_DIR, 'TrieDelTempFile.txt')

    def __init__(self, editor):
        self.editor = editor
        # self.lang = "bo"
        # self.mode = "default"
        # self.tagger = None
        self.matcher = Matchers.expertaRuleMatcher()
#         from storage.models import Token as TokenModel
#         with open(self.TRIE_ADD_TEMP_FILE, 'w', encoding="utf-8") as f:
#             f.write('\n'.join([
#                 '{} {}'.format(d.text, d.pos)
#                 for d in TokenModel.objects.filter(
#                     type=TokenModel.TYPE_UPDATE) if d.pos is not None
#             ]))
#
#         with open(self.TRIE_DEL_TEMP_FILE, 'w', encoding="utf-8") as f:
#             f.write('\n'.join([
#                 '{} {}'.format(d.text, d.pos)
#                 for d in TokenModel.objects.filter(
#                     type=TokenModel.TYPE_REMOVE) if d.pos is not None
#             ]))

        # filter tokens added to the db
        tokenModels = TokenModel.objects.filter(
            type=TokenModel.TYPE_UPDATE)
        # import db tokens into tokenDict
        self.tokenDict = {
            tokenModel.text: tokenModel for tokenModel in tokenModels}


    @property
    def view(self):
        return self.editor.view

    @property
    def tokens(self):
        return self.editor.tokens

    @timed(unit='ms', name='TokenManager.segment: ')
    def segment(self, string):
        tokens = self.editor.tokenizer.tokenize(string, spaces_as_punct=True)

#         logger.debug(str(tokens))

        return TokenList([Token(t) for t in tokens])

    def _join(self, tokens, toStr, sep):
        result = []
        lenOfTokens = len(tokens)
        for i, token in enumerate(tokens):
            result.append((toStr(token) + sep) if i != lenOfTokens - 1
                       else toStr(token))
        result = ''.join(result)

        return result

    @timed(unit='ms', name='getString: ')
    def getString(self):
        if self.view == ViewManager.PLAIN_TEXT_VIEW:
            return self._join(self.tokens, lambda t: t.text, sep='')

        elif self.view == ViewManager.SPACE_VIEW:
            return self._join(self.tokens, lambda t: t.text, sep=' ')

        elif self.view == ViewManager.TAG_VIEW:
        # virtual default tag+space, tag and space should be
        #     return _join(self.tokens, lambda t: t.text + '࿚' + t.pos, sep='')
            return self._join(self.tokens, lambda t: t.text + '࿚' + t.pos, sep='  ')
        else:
            return self._join(self.tokens, lambda t: t.text + '࿚' + t.pos, sep='  ')

    @timed(unit='ms')
    def find(self, position):
        for i, token in enumerate(self.tokens):
            if position in range(token.start, token.end):
                return i, token

    def findByBlockIndex(self, blockIndex):
        startIndex, endIndex = None, None
        for i, token in enumerate(self.tokens):
            if startIndex is None:
                if token.blockIndex == blockIndex:
                    startIndex = i
                    endIndex = i
            elif token.blockIndex == blockIndex:
                endIndex = i
        return startIndex, endIndex

    @timed(unit='ms')
    def matchRules(self):
        # rules = Rule.objects.all()
        # self.matcher.match(self.tokens, rules)
        pass

    @timed(unit='ms')
    def applyDict(self, startToken=None, endToken=None):
        if startToken and endToken:
            tokens = self.tokens[startToken:endToken + 1]
        else:
            tokens = self.tokens

        for token in tokens:
            tokenModel = self.tokenDict.get(token.text_unaffixed)

            if tokenModel is None:
                tokenModel = self.tokenDict.get(token.textWithoutTsek)

            if tokenModel is not None:
                token.applyTokenModel(tokenModel)

    @timed(unit='ms', name='editor.diff: ')
    def diff(self, tokens, oldText, newText):
        #if (oldText and not tokens) or (not oldText and tokens):
        #    raise RuntimeError("old text and tokens not consistent.")

        changes = diff(oldText, newText, timelimit=0, checklines=False,
                               counts_only=False)
        # changes = [('=', 'རྒྱ་ག'), ('-', 'ར'), ('=', '་སྐད་དུ། བོ་དྷི་ས་ཏྭ་ཙརྱ་ཨ་བ་ཏ་ར།')]

        if len(changes) == 1: # 等於 1，表示情況只有「刪除、新增、不變」某一種
            return 0, 0, ''

        oldString = ''
        newString = ''
        sameStringLength = 0
        changePosList = []
        isDeleteShey = False
        isDeleteLastShey = False
        sheyIsMoreThanOne = False
        i = 0
        for op, string in changes:
            if op == "-" or op == "+":
                if not sameStringLength:
                    sameStringLength = 0
                if op == "+":
                    newString = newString + string
                    lastWordIndex = (sameStringLength - 1)
                    # 加在最後面時
                    if '།' in oldString:
                        start = oldString.find('།', lastWordIndex)
                        if string == '།':
                            start += 1
                    elif '\n' in oldString: # 使用 \n 時的時候
                        start = oldString.find('\n', lastWordIndex)
                        if string == '\n':
                            start += 1
                    else:
#                         start = oldString.find('་', lastWordIndex)
                        start = -1

                    if start == -1: # 加在某處時
                        newStringLength = len(newString)
                        if '།' in oldString:
                            start = oldString.rfind('།', 0, newStringLength)
                        elif '\n' in oldString: # 使用 \n 時的時候
                            start = oldString.rfind('\n', 0, newStringLength)
                        else:
#                             start = oldString.rfind('་', 0, newStringLength)
                            start = -1

                    changePos = len(oldString)
                    changePosList.append(changePos)
                    # 當是加入 ། 時，換的位置+1，讓後面找 endNew 時不會用到現在加的
                    if string == '།':
                        changePos += 1
                        changePosList.append(changePos)
                    # 當增加很多文字時， ། 在其中有很多個，需要找到最後一個
                    numOfShey = string.count('།')
                    if numOfShey > 1:
                        sheyIsMoreThanOne = True
                else:
                    if i == 0:
                        start = 0
                    oldString = oldString + string
                    newStringLength = len(newString)
                    if '།' in oldString:
                        start = oldString.rfind('།', 0, newStringLength)
                    elif '\n' in oldString: # 使用 \n 時的時候
                        start = oldString.rfind('\n', 0, newStringLength)
                    else:
#                         start = oldString.rfind('་', 0, newStringLength)
                        start = -1

                    # op == "-" 時才找得到
                    changePos = oldString.find(string, sameStringLength - 1)
                    changePosList.append(changePos)
                    # 當是刪除 ། 時，且所在位置前一個非 ། 無，換的位置-1，讓後面找 endOld 時不會用到現在的
                    if string == '།' and changes[i-1][1][-1] != '།':
                        isDeleteShey = True

                    # 當刪除很多文字時， ། 在其中有很多個，需要找到最後一個
                    numOfShey = string.count('།')
                    if numOfShey > 1:
                        sheyIsMoreThanOne = True

                    # 當刪除的地方在最後而且又是 །
                    if i + 1 == len(changes):
                        if string == '།':
                            isDeleteLastShey = True

                if start == -1: # 改的地方前面沒有'།'或'\n'
                    start = 0
            else:
                sameStringLength = len(string)
                oldString = oldString + string
                newString = newString + string

            i += 1


        changePosForLastOne = max(changePosList)
        changePosForFirstOne = min(changePosList)
        # 往後 scan ，結束位置
        endOld = oldString.find('།', changePosForLastOne)
        endNew = newString.find('།', changePosForLastOne)
        if (endOld == -1 and endNew == -1) or sheyIsMoreThanOne:
            endOld = len(oldString) - 1
            endNew = len(newString) - 1
        #當 ། 有很多個同時在一起時
        if endOld == endNew:
            endOld += 1
        if isDeleteShey and not isDeleteLastShey:
            endOld = endNew + 1
        if isDeleteLastShey:
            endNew = endOld - 1
        if changePosForFirstOne == -1: # 表示為最一開始刪除
            start = 0

        # 讓他可以找到最初的 start
        start = changePosForFirstOne

        # 在文章最後面加字
        if ((changePosForLastOne == tokens[-1].end) or (changePosForLastOne == -1)) \
            and len(changePosList) == 1:
            if (tokens[-1].end == changePosForLastOne):
                start = len(oldString)
            tokenLength = len(tokens)
            tokenStart, tokenEnd = tokenLength, tokenLength

        else: # 修改處字串的開始到結束，找是 token 的哪裡開始到哪裡結束
            # 找 tokenStart
            i = 0
            tokenStart = 0
            for e in tokens:
                if e.start <= start and e.end >= start:
                    if e.end == start:
                        tokenStart = i + 1
                        break
                    else:
                        tokenStart = i
                        break
                i += 1
            # 找 tokenEnd
            i = 0
            tokenEnd = len(tokens) - 1
            for e in tokens:
                if e.start <= endOld and e.end >= endOld:
                    lenOfToken = len(tokens)
                    if i != (lenOfToken - 1):
                        if tokens[i + 1].start == endOld:
                            tokenEnd = i + 1
                            break
                        else:
                            tokenEnd = i
                            break
                i += 1

        # 前後 scan 得到的修改後字串
        afterChangingString = newText[start: endNew + 1]

        if len(tokens) > tokenStart and afterChangingString != '།':
            # 當 tokens 裡為 །། 時，afterChangingString 要多加 ། 在最前面，不然取代掉時會少
            if '།།' == tokens[tokenStart].text:
                afterChangingString = f'།{afterChangingString}'

        return tokenStart, tokenEnd, afterChangingString
