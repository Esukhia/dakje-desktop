
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont

class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highLightBlockOn = False
        self.words = []
        self.formats = {}

        # # grammar
        # grammarFormat = QTextCharFormat()
        # grammarFormat.setForeground(Qt.red)
        # grammarFormat.setFontWeight(QFont.Bold)
        # grammarPatterns = open('files/rules.txt',
        #                        encoding='utf-8').read().strip().split('\n')
        # self.highlightingRules = [(QRegExp(pattern), grammarFormat)
        #                           for pattern in grammarPatterns]
        #
        # # Quotation
        # quotationFormat = QTextCharFormat()
        # quotationFormat.setForeground(Qt.darkYellow)
        # self.highlightingRules.append((QRegExp("\".*\""), quotationFormat))
        #
        # # Random
        # functionFormat = QTextCharFormat()
        # functionFormat.setFontItalic(True)
        # functionFormat.setForeground(Qt.blue)
        # self.highlightingRules.append((QRegExp("yo"), functionFormat))

        # level

        self.formats['level1'] = QTextCharFormat()
        self.formats['level1'].setForeground(Qt.blue)
        self.formats['level1'].setFontWeight(QFont.Bold)

        self.formats['level2'] = QTextCharFormat()
        self.formats['level2'].setForeground(Qt.darkGreen)
        self.formats['level2'].setFontWeight(QFont.Bold)

        self.formats['level3'] = QTextCharFormat()
        self.formats['level3'].setForeground(Qt.darkMagenta)
        self.formats['level3'].setFontWeight(QFont.Bold)

        self.formats['partOfSpeech'] = QTextCharFormat()
        self.formats['partOfSpeech'].setForeground(Qt.lightGray)
        self.formats['partOfSpeech'].setFontWeight(QFont.Light)

        self.formats['level0'] = QTextCharFormat()

    def setFormatColor(self, name, qtColor):
        self.formats[name].setForeground(qtColor)

    def getFormatColor(self, name):
        return self.formats[name].foreground()

    def checkLevel(self, words):
        for word in words:
            word.level = self.wordsLevelDict.get(word.content, None)

    def setWords(self, words):
        self.words = words

    def setHighLightBlock(self, bool):
        self.highLightBlockOn = bool

    def highlightBlock(self, p_str=None):
        if not self.highLightBlockOn:
            return

        for word in self.words:
            self.setFormat(word.start, len(word.content),
                           self.formats['level' + str(word.level)])

            if word.tagIsOn:
                self.setFormat(word.partOfSpeechStart, word.partOfSpeechLen,
                               self.formats['partOfSpeech'])
