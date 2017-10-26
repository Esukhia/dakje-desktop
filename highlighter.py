
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont

class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, mainWindow=None):
        super().__init__(parent)
        self.mainWindow = mainWindow
        self.textFormatManager = self.mainWindow.textFormatManager
        self.highLightBlockOn = False
        self.words = []
        self.formatList = []

    def highlightBlock(self, text):
        if not self.highLightBlockOn:
            return

        for textFormat in self.textFormatManager.getFormats():
            textFormat.counter = 0

        wordFormatDict = self.textFormatManager.getWordFormatDict()
        defaultFormat = self.textFormatManager.getDefaultFormat()
        partOfSpeechFormat = self.textFormatManager.getPartOfSpeechFormat()

        for word in self.words:
            textFormat = wordFormatDict.get(word.content, defaultFormat)
            self.setFormat(word.start, word.length, textFormat)
            textFormat.counter += 1

            if word.tagIsOn:
                self.setFormat(word.end, word.partOfSpeechLen,
                               partOfSpeechFormat)

        for textFormat in self.textFormatManager.getFormats():
            for pattern in textFormat.regexList:
                expression = QRegExp(pattern)
                index = expression.indexIn(text)
                while index >= 0:
                    length = expression.matchedLength()
                    self.setFormat(index, length, textFormat)
                    textFormat.counter += 1
                    index = expression.indexIn(text, index + length)

        self.mainWindow.counterWidget.refresh()
