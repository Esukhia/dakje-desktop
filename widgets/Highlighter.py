from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QThreadPool, QRunnable
from horology import timed
import threading
from PyQt5.Qt import QTextCursor, QTextDocument, QTextLayout
from web.settings import createLogger

logger = createLogger(__name__, "Highlighter.txt")

class Highlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent, editor):
        super().__init__(parent)
        self.editor = editor

    @timed(unit='ms')
    def highlightBlock(self, text):
#         logger.debug(text)
        currentBlock = self.currentBlock()
        currentBlockNumber = currentBlock.blockNumber()
        lastTextEnd = currentBlock.position() - 1 # 當前 block 第一個字，在文章中的位置
        if lastTextEnd == -1:
            lastTextEnd = 0
        textLength = len(text) # 當前 block 文字長度

        tokenStart = 0
        tokenEnd = 0
        currentTokenLen = len(self.editor.tokens)
        if text and self.editor.tokens:
            if currentBlockNumber != 0: # 非第一個 block，tokenStart 不是從 0 開始
                for token in self.editor.tokens:
                    if lastTextEnd <= token.end:
                        tokenStart = tokenStart + 1
                        break
                    tokenStart += 1

            if tokenStart <= currentTokenLen - 1:
                tokensLength = 0
                textEndPos = self.editor.tokens[tokenStart].start + textLength
                for token in self.editor.tokens[tokenStart:]:
                    # 表示 text 結束在這個 token
                    if token.start <= textEndPos <= token.end:
                        if tokenStart == 0:
                            tokenEnd = tokenEnd
                        else:
                            tokenEnd = tokenStart + tokenEnd
                        break
                    tokenEnd += 1

#                 if tokenEnd <= currentTokenLen - 1:
#                     logger.debug(f"{tokenStart}~{tokenEnd}")
#                     logger.debug(f"{self.editor.tokens[tokenStart].text} ~ {self.editor.tokens[tokenEnd].text}")

        else:# 沒有 text 和 tokens 時，不 highlight
            return

        if self.editor.isLevelMode():
            # 編輯器右半邊，使用者選擇了什麼 level
            highlightedLevels = self.editor.getHighlightedLevels()
            for token in self.editor.tokens[tokenStart:tokenEnd + 1]:
                # 根據 level 得到 format(顏色)
                format = self.editor.formatManager.LEVEL_FORMATS[token.level]

                if self.editor.viewManager.isTagView():
                    # format text string
                    textLen = len(token.text)
                    if token.start == 0:
                        textStart = (token.start - currentBlock.position())
                    else:
                        textStart = tagStart + tagSpan + 1
                    textSpan = textLen
                    if token.level in highlightedLevels:
                        self.setFormat(textStart, textSpan, format)

                    # format tags
                    tagFormat = self.editor.formatManager.TAG_FORMAT
                    tagStart = textStart + textSpan + 1
                    tagSpan = 1 + len(token.pos)
                    self.setFormat(tagStart, tagSpan, tagFormat)

                elif self.editor.viewManager.isSpaceView():
                    index = self.editor.tokens.index(token)
                    if token.start == 0:
                        textStart = (token.start - currentBlock.position())
                    else:
                        textStart = (token.start - currentBlock.position()) + index

                    if token.level in highlightedLevels:
                        self.setFormat(textStart, token.length+1, format)

                else: # 可輸入文字的 View
                    # only format what's in the level lists
                    if token.level in highlightedLevels:
                        self.setFormat(
                            token.start - currentBlock.position(), token.length, format)

        # else:  # editor mode
            # highlightedPoses = self.editor.getHighlightedPoses()
            # for token in self.editor.tokens:
            #     if token.pos not in highlightedPoses:
            #         continue
            #     self.setFormat(
            #         token.start - currentBlock.position(), token.length,
            #         self.editor.formatManager.POS_FORMATS[
            #             self.editor.getPosRank(token.pos)]
            #     )
