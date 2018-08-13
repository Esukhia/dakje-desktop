
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont


def getText(words, mode):
    if mode not in ('plainText', 'taggedText'):
        raise NotImplementedError()

    result = ''
    for w in words:
        if mode == 'plainText':
            w.plainTextModePosition = len(result)
            result += w.content
        else:
            w.taggedModePosition = len(result)
            result += w.content + '/' + w.partOfSpeech
    return result


def getWord(position, words, mode):
    if mode not in ('plainText', 'taggedText'):
        raise NotImplementedError()

    for w in words:
        if mode == 'plainText':
            start = w.plainTextModePosition
            end = w.plainTextModePosition + len(w.content)
        else:
            start = w.taggedModePosition
            end = w.taggedModePosition + len(w.content) + w.partOfSpeechLen

        if start <= position < end:
            return w


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

        for w in wordsToHighlight:
            w.highlighted = {}

        plainText = getText(wordsToHighlight, 'plainText')
        taggedText = getText(wordsToHighlight, 'taggedText')

        for textFormat in self.textFormatManager.getFormats():
            if textFormat.type == 'level':
                for pattern in textFormat.regexList:
                    expression = QRegExp(pattern)
                    index = expression.indexIn(plainText)
                    while index >= 0:
                        length = expression.matchedLength()
                        for i in range(length):
                            word = getWord(index + i, wordsToHighlight, 'plainText')
                            if word:
                                word.highlighted[index - word.plainTextModePosition + i] = textFormat
                        index = expression.indexIn(plainText, index + length)
                        textFormat.counterDict[
                            str(currentBlock.blockNumber())] += 1
            else:
                for pattern in textFormat.regexList:
                    expression = QRegExp(pattern)
                    index = expression.indexIn(taggedText)
                    while index >= 0:
                        length = expression.matchedLength()
                        for i in range(length):
                            word = getWord(index + i, wordsToHighlight, 'taggedText')
                            if word:
                                word.highlighted[index - word.taggedModePosition + i] = textFormat
                        index = expression.indexIn(taggedText, index + length)
                        textFormat.counterDict[
                            str(currentBlock.blockNumber())] += 1

        for word in wordsToHighlight:
            for index, textFormat in word.highlighted.items():
                if self.mainWindow.modeManager.isTagMode():
                    if index >= word.length + word.partOfSpeechLen:
                        break

                else:
                    if index >= word.length:
                        break

                self.setFormat(word.start - start + index, 1, textFormat)

            textFormat = word.needHighlighted()
            if textFormat:
                self.setFormat(word.start - start, word.length, textFormat)

        self.mainWindow.counterWidget.refresh()
