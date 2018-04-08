
from PyQt5.QtGui import QTextCharFormat

class TextFormat(QTextCharFormat):
    def __init__(self, name, type):
        super().__init__()
        self.name = name
        self.wordList = []
        self.regexList = []
        self.type = type  # level or pos

        self.nameLabel = None
        self.colorButton = None
        self.listButton = None
        self.ruleButton = None
        self.counterLabel = None

    def setupWordList(self, listPath, lines=None):
        self.wordList = []

        if lines:
            lines = lines
        else:
            with open(listPath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

        for line in lines:
            word = line.rstrip()
            if not word:
                continue
            # add a tsek where missing
            if not word.endswith('་'):
                word += '་'
            self.wordList.append(word)

    def setupRegexList(self, regexPath, lines=None):
        self.regexList = []

        if lines:
            lines = lines
        else:
            with open(regexPath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

        for line in lines:
            regex = line.rstrip()
            if regex:
                self.regexList.append(regex)

    def getColorRgbaCss(self):
        return 'rgba({}, {}, {})'.format(
            *(self.foreground().color().getRgb()))

    def getColorRgba(self):
        return self.foreground().color().getRgb()

    def setColor(self, qtColor):
        self.setForeground(qtColor)

    def getColor(self):
        return self.foreground().color()
