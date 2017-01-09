
import PyQt5
from PyQt5.QtCore import QFile, QRegExp, Qt, QTextStream
from PyQt5.QtGui import (QFont, QIcon, QKeySequence, QSyntaxHighlighter,
                         QTextCharFormat, QTextCursor, QTextTableFormat)
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QDockWidget,
                             QFileDialog, QGridLayout, QLabel, QLineEdit,
                             QListWidget, QMainWindow, QMenu, QMessageBox,
                             QPushButton, QTextEdit, QWidget)


class Highlighter(QSyntaxHighlighter):

    def __init__(self, parent=None, ya=['he', 'he']):
        super(Highlighter, self).__init__(parent)

# Import Test
        yo = ya
        print(yo)

# Basic Spellcheking Rules
        grammarFormat = QTextCharFormat()
        grammarFormat.setForeground(Qt.darkBlue)
        grammarFormat.setFontWeight(QFont.Bold)
        grammarPatterns = [""]

        self.highlightingRules = [(QRegExp(pattern), grammarFormat)
                                  for pattern in grammarPatterns]

# # Level1
#         level1Format = QTextCharFormat()
#         level1Format.setForeground(Qt.darkBlue)
#         level1Format.setFontWeight(QFont.Bold)
#         level1Patterns = ["\\བཀྲ་ཤིས\\b", "\\bha\\b"]

#         self.highlightingRules = [(QRegExp(pattern), level1Format)
#                                   for pattern in level1Patterns]

# # Level2
#         level2Format = QTextCharFormat()
#         level2Format.setForeground(Qt.darkRed)
#         level2Format.setFontWeight(QFont.Bold)
#         keywordPatterns = ["\\bho\\b", "\\bclass\\b"]

#         self.highlightingRules = [(QRegExp(pattern), level2Format)
#                                   for pattern in keywordPatterns]

# Level3
        level3Format = QTextCharFormat()
        level3Format.setForeground(Qt.darkYellow)
        level3Format.setFontWeight(QFont.Bold)
        keywordPatterns = ["\\བཀྲ་\\b", "\\bint\\b","\\bhi\\b"]

        # self.highlightingRules.append((QRegExp(pattern), level3Format))

# Examples
        classFormat = QTextCharFormat()
        classFormat.setFontWeight(QFont.Bold)
        classFormat.setForeground(Qt.darkMagenta)
        self.highlightingRules.append((QRegExp("\\bya\\b"),
                                       classFormat))

        singleLineCommentFormat = QTextCharFormat()
        singleLineCommentFormat.setForeground(Qt.red)
        self.highlightingRules.append(
            (QRegExp("//[^\n]*"), singleLineCommentFormat))

        self.multiLineCommentFormat = QTextCharFormat()
        self.multiLineCommentFormat.setForeground(Qt.red)

        quotationFormat = QTextCharFormat()
        quotationFormat.setForeground(Qt.darkGreen)
        self.highlightingRules.append((QRegExp("\".*\""), quotationFormat))

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