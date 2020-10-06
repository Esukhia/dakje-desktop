from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QThreadPool, QRunnable
from horology import timed
import threading
from PyQt5.Qt import QTextCursor, QTextDocument, QTextLayout

class Highlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent, editor):
        super().__init__(parent)
        self.editor = editor

    @timed(unit='ms')
    def highlightBlock(self, text):
        currentBlock = self.currentBlock()
        currentBlockNumber = currentBlock.blockNumber()
        lastTextEnd = currentBlock.position() - 1 # 當前 block 第一個字，在文章中的位置
        if lastTextEnd == -1:
            lastTextEnd = 0
        textLength = len(text) # 當前 block 文字長度

        tokenStart = 0
        tokenEnd = 0
        if text and self.editor.tokens:
            if currentBlockNumber != 0: # 非第一個 block，tokenStart 不是從 0 開始
                for token in self.editor.tokens:
                    if lastTextEnd <= token.end:
                        tokenStart = tokenStart + 1
                        break
                    tokenStart += 1

            for token in self.editor.tokens[tokenStart:]:
                if self.editor.tokens[tokenStart].start + (textLength - 1) <= \
                    token.end: # 表示 text 結束在這個 token
                    if tokenStart == 0:
                        tokenEnd = tokenEnd
                    else:
                        tokenEnd = tokenStart + tokenEnd + 1
                    break
                tokenEnd += 1
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
#                     tagStart = (
#                         token.start - currentBlock.position()) + textLen
                    tagStart = textStart + textSpan + 1
#                     tagSpan = token.length - textLen
                    tagSpan = 1 + len(token.pos)
                    self.setFormat(tagStart, tagSpan, tagFormat)

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
#         threading.Thread(target=job, args=(self, text)).start()
    @timed(unit='ms')
    def asHtml(self):
        # Create a new document from all the selected text document.
        cursor = QTextCursor(self.document())
        cursor.select(QTextCursor.Document)
        tempDocument = QTextDocument()
        tempCursor = QTextCursor(tempDocument)

        tempCursor.insertFragment(cursor.selection())
        tempCursor.select(QTextCursor.Document)
        # Set the default foreground for the inserted characters.
        textfmt = tempCursor.charFormat()
        textfmt.setForeground(QtCore.Qt.black)
        tempCursor.setCharFormat(textfmt)

        # Apply the additional formats set by the syntax highlighter
        start = self.document().findBlock(cursor.selectionStart())
        end = self.document().findBlock(cursor.selectionEnd())
        end = end.next()
        selectionStart = cursor.selectionStart()
        endOfDocument = tempDocument.characterCount() - 1
        current = start
        while current.isValid() and current != end:
            layout = current.layout()

            for range in layout.additionalFormats():
                start = current.position() + range.start - selectionStart
                end = start + range.length
                if end <= 0 or start >= endOfDocument:
                    continue
                tempCursor.setPosition(max(start, 0))
                tempCursor.setPosition(min(end, endOfDocument), QTextCursor.KeepAnchor)
                tempCursor.setCharFormat(range.format)

            current = current.next()

        # Reset the user states since they are not interesting
        block = tempDocument.begin()
        while block.isValid():
            block.setUserState(-1)
            block = block.next()

        # Make sure the text appears pre-formatted, and set the background we want.
        tempCursor.select(QTextCursor.Document)
        blockFormat = tempCursor.blockFormat()
        blockFormat.setNonBreakableLines(True)
        blockFormat.setBackground(QtCore.Qt.white)
        tempCursor.setBlockFormat(blockFormat)

        # Finally retreive the syntax higlighted and formatted html.
        return tempCursor.selection().toHtml()


