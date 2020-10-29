#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
django.setup()

import unittest
import pybo
import botok
from diff_match_patch import diff
from managers import TokenManager
from managers.TokenManager import TokenList, Token

class MockEditor(unittest.TestCase):

    def __init__(self):
        self.tokenManager = TokenManager(self)
        self.tokens = TokenList()
        self.tokenizer = pybo.WordTokenizer(
            'POS',
            tok_modifs= self.tokenManager.TRIE_MODIF_DIR
        )

class MyToken(Token):
    def __init__(self, text):
        t = botok.tokenizers.token.Token()
        t.text = text
        super().__init__(t)

class TokenListTest(unittest.TestCase):

    def getTokenLists(self):
        self.tokenOld = MyToken('abc')
        self.token = MyToken('p')
        oldTokenL = TokenList([self.tokenOld])
        tokenL = TokenList([self.token])
        return oldTokenL, tokenL

    def testSet(self):
        oldTokenL, tokenL = self.getTokenLists()
        oriOldTokenL = oldTokenL.copy()
        oldEnd = oldTokenL[-1].end
        answer = 1 # 答案是 1(因為換一個字 p)
        oldTokenL[0:1] = tokenL
        newEnd = oldTokenL[-1].end
        self.assertEqual(newEnd, answer)

        oldTokenL = oriOldTokenL.copy()
        oldTokenL[0] = tokenL[0]
        newEnd = oldTokenL[-1].end
        self.assertEqual(newEnd, answer)

        oldTokenL = oriOldTokenL.copy()
        oldTokenL[-1] = tokenL[0]
        newEnd = oldTokenL[-1].end
        self.assertEqual(newEnd, answer)

        answer = 3 # 答案是 1(因為換一個字 p)
        oldTokenL.append(tokenL)
        oldTokenL[-2:] = oriOldTokenL
        newEnd = oldTokenL[-1].end
        self.assertEqual(newEnd, answer)

    def testAppend(self):
        oldTokenL, tokenL = self.getTokenLists()
        oldEnd = oldTokenL[-1].end
        answer = oldEnd + 1 # 答案是原本的 end + 1(因為再多加一個字串 p)
        oldTokenL.append(tokenL)
        newEnd = oldTokenL[-1].end
        self.assertEqual(newEnd, answer)

    def testInsert(self):
        oldTokenL, tokenL = self.getTokenLists()
        oldEnd = oldTokenL[-1].end
        answer = oldEnd + 1 # 答案是原本的 end + 1(因為再多加一個字串 p)
        oldTokenL.insert(1, tokenL)
        newEnd = oldTokenL[-1].end
        self.assertEqual(newEnd, answer)

    def testDel(self):
        oldTokenL, tokenL = self.getTokenLists()
        oldTokenL.insert(1, tokenL)
        del oldTokenL[1]
        answer = 3 # 答案是一個字串 abc 長度
        newEnd = oldTokenL[-1].end
        self.assertEqual(newEnd, answer)

    def testRemove(self):
        oldTokenL, tokenL = self.getTokenLists()
        oldTokenL.insert(1, tokenL)
        oldTokenL.remove(self.token)
        answer = 3 # 答案是一個字串 abc 長度
        newEnd = oldTokenL[-1].end
        self.assertEqual(newEnd, answer)

    def testExtend(self):
        oldTokenL, tokenL = self.getTokenLists()
        oldEnd = oldTokenL[-1].end
        answer = oldEnd + 1 # 答案是原本的 end + 1(因為再多加一個字串 p)
        oldTokenL.extend(tokenL)
        newEnd = oldTokenL[-1].end
        self.assertEqual(newEnd, answer)

    def testPop(self):
        oldTokenL, tokenL = self.getTokenLists()
        oldTokenL.insert(1, tokenL)
        oldTokenL.pop(1)
        answer = 3 # 答案是一個字串 abc 長度
        newEnd = oldTokenL[-1].end
        self.assertEqual(newEnd, answer)

    def testClear(self):
        oldTokenL = self.getTokenLists()[0]
        oldTokenL.clear()
        self.assertEqual(oldTokenL, [])

    def testCopy(self):
        oldTokenL = self.getTokenLists()[0]
        copyTokenL = oldTokenL.copy()
        self.assertEqual(oldTokenL, copyTokenL)

    def testCount(self):
        oldTokenL = self.getTokenLists()[0]
        with self.assertRaises(RuntimeError):
            count = oldTokenL.count(oldTokenL)


    def testReverse(self):
        oldTokenL = self.getTokenLists()[0]
        with self.assertRaises(RuntimeError):
            oldTokenL.reverse()

    def testSort(self):
        oldTokenL = self.getTokenLists()[0]
        with self.assertRaises(RuntimeError):
            oldTokenL.sort()

class EditorTest(unittest.TestCase):

    def diffAndSegment(self, oldText, newText):
        self.mockEditor = MockEditor()
        self.tokenManager = TokenManager(self.mockEditor)
        tokens = self.tokenManager.segment(oldText)
#         print('前',[f'{e.start}-{e.end}' for e in tokens]) #修改前
        tokenStart, tokenEnd, afterChangingString = \
                    self.tokenManager.diff(tokens, oldText, newText)
        newTokens = self.tokenManager.segment(afterChangingString)

        if tokenStart == tokenEnd and \
            not (tokenStart == 0) and \
            not tokens[-1].text in afterChangingString:
            if newTokens[0] == '།' or newTokens[0] == '\n':
                tokens.extend(newTokens[1:])
            else:
                tokens.extend(newTokens[0:])
        elif tokenStart ==  0 and tokenEnd ==  0:
           tokens = self.tokenManager.segment(oldText)
        else:
            tokens[tokenStart:tokenEnd + 1] = newTokens

#         print('後',[f'{e.start}-{e.end}' for e in tokens]) #修改後

        afterEditText = ''.join([e.text for e in tokens])

        return afterEditText, tokens

    def testText(self):
        old = '༅། །འདིར་བདག་།།།།།།།ཅག་གི་སྟོན་པ་ཡང་དག་པར་རྫོགས་པའི་སངས་རྒྱས་བཅོམ་ལྡན་འདས་ཐབས་ལ་མཁས་ཤིང་ཐུགས་རྗེ་ཚད་མེད་པ་དང་ལྡན་པ་དེ་ཉིད་ཀྱིས་ཐུན་མོང་དང་ཐུན་མོང་མིན་པའི་དམ་པའི་ཆོས་ཀྱི་སྒོ་མཐའ་ཡས་ཤིང་བསམ་གྱིས་མི་ཁྱབ་པ། བསྟན་པ་མཐའ་དག་གི་སྙིང་པོར་གྱུར་པ། གསང་སྔགས་རྡོ་རྗེ་ཐེག་པ་བླ་ན་མེད་པའི་རྒྱུད་སྡེ་ཐམས་ཅད་ཀྱི་རྒྱལ་པོ། སངས་རྒྱས་ཐམས་ཅད་ཀྱི་སྙིང་པོའི་དཀྱིལ་འཁོར། དཔལ་དགྱེས་པ་རྡོ་རྗེའི་རྩ་བའི་རྒྱུད་བརྟག་པ་གཉིས་པའི་སྤྱི་དོན། དགྱེས་མཛད་སྤྲུལ་པའི་སྐུ་མར་རྔོག་ཡབ་སྲས་ཀྱི་བཀའ་སྲོལ་ལྟར་མདོ་ཙམ་འཆད་པ་ཡིན་ནོ། །'
        new = '༅། །འདིར་བདག་།།།།།།།ཅག་གི་སྟོན་པ་ཡང་དག་པར་རྫོགས་པའི་སངས་རྒྱས་བཅོམ་ལྡན་འདས་ཐབས་ལ་མཁས་ཤིང་ཐུགས་རྗེ་ཚད་མེད་པ་དང་ལྡན་པ་དེ་ཉིད་ཀྱིས་ཐུན་མོང་དང་ཐུན་མོང་མིན་པའི་དམ་པའི་ཆོས་ཀྱི་སྒོ་མཐའ་ཡས་ཤིང་བསམ་གྱིས་མི་ཁྱབ་པ། བསྟན་པ་མཐའ་དག་གི་སྙིང་པོར་གྱུར་པ། གསང་སྔགས་རྡོ་རྗེ་ཐེག་པ་བླ་ན་མེད་པའི་རྒྱུད་སྡེ་ཐམས་ཅད་ཀྱི་རྒྱལ་པོ། སངས་རྒྱས་ཐམས་ཅད་ཀྱི་སྙིང་པོའི་དཀྱིལ་འཁོར། དཔལ་དགྱེས་པ་རྡོ་རྗེའི་རྩ་བའི་རྒྱུད་བརྟག་པ་གཉིས་པའི་སྤྱི་དོན། དགྱེས་མཛད་སྤྲུལ་པའི་སྐུ་མར་རྔོག་ཡབ་སྲས་ཀྱི་བཀའ་སྲོལ་ལྟར་མདོ་ཙམ་འཆད་པ་ཡིན་ནོ། །'
        self.assertEqual(old, new)

    def testDiff(self): # 某處修改
        oldText = "རྒྱ་གར་སྐད་དུ། བོ་དྷི་ས་ཏྭ་ཙརྱ་ཨ་བ་ཏ་། བོད་སྐད་དུ།"
        newText = "རྒྱ་ག་སྐད་དུ། བོ་དྷི་ས་ཏྭ་ཙརྱ་ཨ་བ་ཏ་། བོད་སྐད་དུ།"
        afterEditText = self.diffAndSegment(oldText, newText)[0]
        self.assertEqual(afterEditText, newText)

    def testDiff2(self): # 最後加字
        oldText = "རྒྱ་གར་སྐད་དུ། བོ་དྷི་ས་ཏྭ་ཙརྱ་ཨ་བ་ཏ་ར། བོད་སྐད་དུ།"
        newText = "རྒྱ་གར་སྐད་དུ། བོ་དྷི་ས་ཏྭ་ཙརྱ་ཨ་བ་ཏ་ར། བོད་སྐད་དུ། ཙརྱ་ཨ་བ་།"
        afterEditText = self.diffAndSegment(oldText, newText)[0]
        self.assertEqual(afterEditText, newText)

    def testDiff3(self): # 某處加字
        oldText = "རྒྱ་གར་སྐད་དུ། བོ་དྷི་ས་ཏྭ་ཙརྱ་ཨ་བ་ཏ་ར། བོད་སྐད་དུ།"
        newText = "རྒྱ་གར་སྐད་དུ། བོ་དྷི་ས་ཏྭ་ཙརྱ་ཨ་བ་ཏ་རརར། བོད་སྐད་དུ།"
        afterEditText = self.diffAndSegment(oldText, newText)[0]
        self.assertEqual(afterEditText, newText)

    def testDiff4(self): # 連續修改
        oldText = "རྒྱ་གར་སྐད་དུ། བོ་དྷི་ས་ཏྭ་ཙརྱ་ཨ་བ་ཏ་། བོད་སྐད་དུ།"
        newText = "རྒྱ་ག་སྐད་དུ། བོ་དྷི་ས་ཏྭ་ཙརྱ་ཨ་བ་ཏ་། བོད་སྐད་དུ།"
        afterEditText, tokens = self.diffAndSegment(oldText, newText)

        # 第二次修改
        oldText = afterEditText
        newText = "རྒྱ་ག་སྐད་དུ། བོ་དྷི་ས་ཏྭ་ཙརྱ་ཨ་བ་ཏ་། བོ་སྐད་དུ།"
#         print('前',[f'{e.start}-{e.end}' for e in tokens]) #修改前
        tokenStart, tokenEnd, afterChangingString = \
                    self.tokenManager.diff(tokens, oldText, newText)
        newTokens = self.tokenManager.segment(afterChangingString)

        if tokenStart == tokenEnd and \
            not (tokenStart == 0) and \
            not tokens[-1].text in afterChangingString:
            if newTokens[0] == '།' or newTokens[0] == '\n':
                tokens.extend(newTokens[1:])
            else:
                tokens.extend(newTokens[0:])
        elif tokenStart ==  0 and tokenEnd ==  0:
            tokens = self.tokenManager.segment(oldText)
        else:
            tokens[tokenStart:tokenEnd + 1] = newTokens

#         print('後',[f'{e.start}-{e.end}' for e in tokens]) #修改後

        afterEditText = ''.join([e.text for e in tokens])

        self.assertEqual(afterEditText, newText)

if __name__ == '__main__' :
    unittest.main()

