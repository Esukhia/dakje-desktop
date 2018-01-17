
from Word import Word

from PyQt5.QtWidgets import QPlainTextEdit, QMessageBox, QScrollBar

class EventHandler:
    def __init__(self, parent):
        self.parent = parent
        self.changedWithoutSaving = False

        self.curPos = 0
        self.prePos = 0

        self.preStart = None
        self.preEnd = None
        self.curStart = None
        self.curEnd = None

    def cursorPositionChanged(self):
        textEdit = self.parent.textEdit

        # 更新現在位置
        cursor = textEdit.textCursor()
        self.prePos = self.curPos
        self.curPos = cursor.position()
        self.preStart = self.curStart
        self.preEnd = self.curEnd

        if cursor.hasSelection():
            self.curStart = cursor.selectionStart()
            self.curEnd = cursor.selectionEnd()
        else:
            self.curStart = None
            self.curEnd = None

    def textChanged(self):
        textEdit = self.parent.textEdit
        wordManager = self.parent.wordManager
        text = self.parent.textEdit.toPlainText()
        shift = self.curPos - self.prePos

        if not textEdit.toPlainText() or self.preStart == 0:
            wordManager.setWords([])

        # plain text mode:
        if not self.parent.modeManager.isSpaceMode():
            if self.preStart:
                wordManager.removeWords(self.preStart, self.preEnd)
                for word in wordManager.getWords(start=self.prePos):
                    word.start += shift
            else:
                wordManager.removeWord(self.prePos)
                for word in wordManager.getWords(start=self.prePos):
                    word.start += shift

        # space mode:
        # 空白模式時，因為不能重segment，預設只是改空白而已
        else:
            for word in wordManager.getWords(start=self.prePos):
               word.start += shift
            wordManager.reSegmentWord(self.curPos, self.prePos, text)

        self.parent.highlightViewpoint()
        self.changedWithoutSaving = True
        self.checkTitle()
    
    def checkTitle(self):
        if self.changedWithoutSaving:
            if not self.parent.windowTitle().endswith('*'):
                self.parent.setWindowTitle(self.parent.windowTitle() + '*')
        else:
            if self.parent.windowTitle().endswith('*'):
                self.parent.setWindowTitle(
                    self.parent.windowTitle()[:-1])

    def mousePressEvent(self, event):
        QPlainTextEdit.mousePressEvent(self.parent.textEdit, event)

        if self.parent.modeManager.isTagMode():
            self.parent.selectedWord = self.parent.wordManager.getPartOfSpeechWord(
                self.parent.textEdit.textCursor().position())

            if self.parent.selectedWord:
                self.parent.changeTag(event.pos())

    def wheelEvent(self, event):
        QPlainTextEdit.wheelEvent(self.parent.textEdit, event)
        self.parent.highlightViewpoint()

    def checkSaving(self):
        if self.changedWithoutSaving:
            reply = QMessageBox.question(
                self.parent, 'Save', 'Save the file?',
                QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.parent.saveFile()
            else:
                pass

    def sliderChange(self, event):
        QScrollBar.mouseReleaseEvent(
            self.parent.textEdit.verticalScrollBar(), event)
        self.parent.highlightViewpoint()

