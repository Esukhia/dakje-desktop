
import PyQt5
from PyQt5.QtCore import QFile, QRegExp, Qt, QTextStream
from PyQt5.QtGui import (QFont, QIcon, QKeySequence, QSyntaxHighlighter,
                         QTextCharFormat, QTextCursor, QTextTableFormat)
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QDockWidget,
                             QFileDialog, QGridLayout, QLabel, QLineEdit,
                             QListWidget, QMainWindow, QMenu, QMessageBox,
                             QPushButton, QTextEdit, QWidget)


class Highlighter(QSyntaxHighlighter):
# This class applies the content of the highlightingRules list to a document.
# List structure: [regex, format, regex, format, ...]

    def __init__(self, parent=None, listsDict={'level0': ['he', 'he']}):
        super(Highlighter, self).__init__(parent)

# Import Test
# TODO: lower grammarFormat to the end of the method, so it overwrites other highlights
        # yo = listsDict
        # print(yo)

# Basic Spellcheking Rules
        grammarFormat = QTextCharFormat()
        grammarFormat.setForeground(Qt.red)
        grammarFormat.setFontWeight(QFont.Bold)
        # grammarPatterns = ["([^གང]་གིས[་༌།༎༏༐༑༔]+|[^ནམརལ]་གྱིས[་༌།༎༏༐༑༔\s]+(?!ཤིག|ལ))", "yay"]
        grammarPatterns = open('files/rules.txt').read().strip().split('\n')

        self.highlightingRules = [(QRegExp(pattern), grammarFormat)
                                  for pattern in grammarPatterns]


# Level1: creates a font format, pairs it to regexes and adds these pairs to the list.
        level1Format = QTextCharFormat()
        level1Format.setForeground(Qt.blue)
        level1Format.setFontWeight(QFont.Bold)
# Find the list called "Level1" in the dict and give it to level1Regexes
        level1Regexes = listsDict['Level1']

        self.level1Patterns = [(QRegExp(pattern), level1Format)
                                  for pattern in level1Regexes]
        self.highlightingRules.extend(self.level1Patterns)

# Level2
        level2Format = QTextCharFormat()
        level2Format.setForeground(Qt.darkGreen)
        level2Format.setFontWeight(QFont.Bold)
        level2Regexes = listsDict['Level2']

        self.level2Patterns = [(QRegExp(pattern), level2Format)
                                  for pattern in level2Regexes]
        self.highlightingRules.extend(self.level2Patterns)

# Level3
        level3Format = QTextCharFormat()
        level3Format.setForeground(Qt.darkMagenta)
        level3Format.setFontWeight(QFont.Bold)
        level3Regexes = listsDict['Level3']

        self.level3Patterns = [(QRegExp(pattern), level3Format)
                                  for pattern in level3Regexes]
        self.highlightingRules.extend(self.level3Patterns)


# Quotation 

        quotationFormat = QTextCharFormat()
        quotationFormat.setForeground(Qt.darkYellow)
        self.highlightingRules.append((QRegExp("\".*\""), quotationFormat))

# Random
        functionFormat = QTextCharFormat()
        functionFormat.setFontItalic(True)
        functionFormat.setForeground(Qt.blue)
        self.highlightingRules.append((QRegExp("yo"),
                                       functionFormat))


    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)




