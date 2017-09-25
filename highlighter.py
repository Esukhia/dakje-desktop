
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont

class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, editor=None):
        super().__init__(parent)

        self.editor = editor
        self.highlightedText = None
        self.formatPositions = []

        self.wordsLevelDict = {}

        for level in range(1, 4):
            with open('files/Lists/General/{0}/General_Level_{0}'.format(
                    level), encoding='utf-8') as f:
                for line in f.readlines():
                    word = line.rstrip('\n')

                    # add a tsek where missing
                    if not word.endswith('་'):
                        word += '་'

                    self.wordsLevelDict[word] = level

        self.formats = {}

        # grammar

        grammarFormat = QTextCharFormat()
        grammarFormat.setForeground(Qt.red)
        grammarFormat.setFontWeight(QFont.Bold)
        grammarPatterns = open('files/rules.txt',
                               encoding='utf-8').read().strip().split('\n')
        self.highlightingRules = [(QRegExp(pattern), grammarFormat)
                                  for pattern in grammarPatterns]

        # Quotation
        quotationFormat = QTextCharFormat()
        quotationFormat.setForeground(Qt.darkYellow)
        self.highlightingRules.append((QRegExp("\".*\""), quotationFormat))

        # Random
        functionFormat = QTextCharFormat()
        functionFormat.setFontItalic(True)
        functionFormat.setForeground(Qt.blue)
        self.highlightingRules.append((QRegExp("yo"), functionFormat))

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

        self.formats['levelNone'] = QTextCharFormat()

    def setFormatColor(self, name, qtColor):
        self.formats[name].setForeground(qtColor)

    def getFormatColor(self, name):
        return self.formats[name].foreground()

    def checkLevel(self, words):
        for word in words:
            word.level = self.wordsLevelDict.get(word.content, None)

    def highlight(self, words, spacesOpened=True, tagsOpened=False, check=False):
        if check:
            self.checkLevel(words)

        highlightedText = []

        self.formatPositions = []

        speechFormat = self.formats['partOfSpeech']

        end = 0

        for word in words:
            start = end
            end = start + len(word.content)

            highlightedText.append(word.content)
            self.formatPositions.append([start, end, self.formats[
                'level' + str(word.level)], word.level])

            if tagsOpened:
                start = end
                end = start + len(word.partOfSpeech) + 1

                word.position = (start + 1, end)

                highlightedText.append('/')
                highlightedText.append(word.partOfSpeech)
                self.formatPositions.append([start, end, speechFormat, word.level])

            if spacesOpened:
                highlightedText.append(' ')
                end += 1

        self.highlightedText = ''.join(highlightedText)

    def disableHighlight(self):
        self.formatPositions = []

    def highlightBlock(self, p_str=None):
        if not self.formatPositions:
            return

        for position in self.formatPositions:
            self.setFormat(position[0], position[1], position[2])

        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(self.highlightedText)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(self.highlightedText, index + length)
