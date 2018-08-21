
import re

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCharFormat, QColor
from PyQt5.QtWidgets import QMessageBox

from functools import partial

class TextFormat(QTextCharFormat):
    def __init__(self, name, type):
        super().__init__()
        self.name = name
        self.wordList = []
        self.regexList = []
        self.type = type  # level or pos

        self.counter = 0
        self.counterDict = {}

        # Tab
        self.tabHBox = None
        self.editButton = None
        self.colorButton = None
        self.listButton = None
        self.ruleButton = None
        self.removeButton = None
        # Counter
        self.counterNameLabel = None
        self.counterHBox = None

        levelColors = {
            'Level1': '#87a840',
            'Level2': '#ddc328',
            'Level3': '#b63226',
            'Level4': '#278da9',
            'Level5': '#363d5c'
        }
        if 'Level' in self.name:
            if self.name in levelColors:
                hex = levelColors[self.name]
            else:
                hex = levelColors['Level3']
            r, g, b = hex[1:3], hex[3:5], hex[5:7]
            self.setColor(QColor(int(r, 16), int(g, 16), int(b, 16)))

    def setupWordList(self, listPath, lines=None):
        self.wordList = []

        if lines:
            lines = lines
        else:
            with open(listPath, encoding='utf-8') as f:
                lines = f.readlines()

        for line in lines:
            word = line.rstrip('\r\n')
            if word:
                # remove a tsek
                if word.endswith('་'):
                    word = word[:-1]
                self.wordList.append(word)

    def setupRegexList(self, regexPath, lines=None):
        self.regexList = []

        if lines:
            lines = lines
        else:
            try:
                with open(regexPath, encoding='utf-8') as f:
                    lines = f.readlines()
            except UnicodeDecodeError as e:
                self.msg = QMessageBox()
                self.msg.setIcon(QMessageBox.Warning)
                self.msg.setText("The rule file should be UTF-8 encoding.")
                self.msg.show()
                return False

        for i, line in enumerate(lines):
            regex = line.rstrip('\r\n')
            if regex:
                try:
                    re.compile(regex)
                    self.regexList.append(regex)
                except Exception as e:
                    self.msg = QMessageBox()
                    self.msg.setIcon(QMessageBox.Warning)
                    self.msg.setText("Invalid regex in line: {}\n{}".format(
                        i + 1, str(e)))
                    self.msg.show()
                    return False
        else:
            return True


    def getColorRgbaCss(self):
        return 'rgba({}, {}, {})'.format(
            *(self.foreground().color().getRgb()))

    def getColorRgba(self):
        return self.foreground().color().getRgb()

    def setColor(self, qtColor):
        self.setForeground(qtColor)

    def getColor(self):
        return self.foreground().color()


class TextFormatManager:
    def __init__(self, parent):
        self.parent = parent
        self._formats = []

        self._defaultTextFormat = TextFormat('default', 'level')
        self._partOfSpeechFormat = TextFormat('partOfSpeech', 'level')
        self._partOfSpeechFormat.setColor(Qt.lightGray)

    def insert(self, textFormat):
        self._formats.append(textFormat)
        self.parent.profileWidget.addTextFormat(textFormat)
        self.parent.counterWidget.addTextFormat(textFormat)

    def remove(self, textFormat):
        self.parent.profileWidget.removeTextFormat(textFormat)
        self.parent.counterWidget.removeTextFormat(textFormat)

        for index, f in enumerate(reversed(self._formats)):
            if f is textFormat:
                self._formats.pop(len(self._formats) - 1 - index)

        self.parent.highlightViewpoint()



    def clear(self):
        for textFormat in self._formats:
            self.parent.profileWidget.removeTextFormat(textFormat)
            self.parent.counterWidget.removeTextFormat(textFormat)
        self._formats = []

    def getFormats(self, type=None):
        if type:
            return [f for f in self._formats if f.type == type]
        return self._formats

    def getWordFormatDict(self):
        wordFormatDict = {}
        for textFormat in self._formats:
            for word in textFormat.wordList:
                wordFormatDict[word] = textFormat

        return wordFormatDict

    def getDefaultFormat(self):
        return self._defaultTextFormat

    def getPartOfSpeechFormat(self):
        return self._partOfSpeechFormat
