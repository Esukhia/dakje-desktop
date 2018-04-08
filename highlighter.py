
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont

class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, mainWindow=None):
        super().__init__(parent)
        self.mainWindow = mainWindow
        self.textFormatManager = self.mainWindow.textFormatManager
        self.highLightBlockOn = False
        self.formatList = []

    def highlightBlock(self, text):
        if not self.highLightBlockOn:
            return

        wordFormatDict = self.textFormatManager.getWordFormatDict()
        defaultFormat = self.textFormatManager.getDefaultFormat()
        partOfSpeechFormat = self.textFormatManager.getPartOfSpeechFormat()
        currentBlock = self.currentBlock()

        for textFormat in self.mainWindow.textFormatManager.getFormats():
            textFormat.counterDict[str(currentBlock.blockNumber())] = 0
        self.mainWindow.textFormatManager.getDefaultFormat().counterDict[
            str(currentBlock.blockNumber())] = 0
        self.mainWindow.textFormatManager.getPartOfSpeechFormat().counterDict[
            str(currentBlock.blockNumber())] = 0

        
        start = currentBlock.position()
        end = start + currentBlock.length()
        wordsToHighlight = self.mainWindow.wordManager.getWords(start, end)

        for word in wordsToHighlight:
            textFormat = wordFormatDict.get(word.content, defaultFormat)

            self.setFormat(word.start - start, word.length, textFormat)

            textFormat.counterDict[str(currentBlock.blockNumber())] += 1

            if word.tagIsOn:
                self.setFormat(word.end - start, word.partOfSpeechLen,
                               partOfSpeechFormat)

        for textFormat in self.textFormatManager.getFormats():
            for pattern in textFormat.regexList:
                expression = QRegExp(pattern)
                index = expression.indexIn(text)
                while index >= 0:
                    length = expression.matchedLength()
                    self.setFormat(index, length, textFormat)
                    index = expression.indexIn(text, index + length)

                    textFormat.counterDict[
                        str(currentBlock.blockNumber())] += 1

        self.mainWindow.counterWidget.refresh()
