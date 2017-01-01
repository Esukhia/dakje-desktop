import PyQt5
from PyQt5.QtCore import QFile, QRegExp, Qt, QTextStream
from PyQt5.QtGui import (QFont, QIcon, QKeySequence, QSyntaxHighlighter,
                         QTextCharFormat, QTextCursor, QTextTableFormat)
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QMenu, QLabel, QLineEdit, QGridLayout,
                             QWidget, QPushButton, QDockWidget, QDialog, QListWidget, QMessageBox, QTextEdit)


class Highlighter(QSyntaxHighlighter):

    def __init__(self, parent=None, yo=""):
        super(Highlighter, self).__init__(parent)

        self.test = yo
        print(self.test)

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(Qt.darkBlue)
        keywordFormat.setFontWeight(QFont.Bold)

        keywordPatterns = ["\\བཀྲ་ཤིས\\b", "\\bclass\\b", "\\bconst\\b",
                           "\\bdouble\\b", "\\benum\\b", "\\bexplicit\\b", "\\bfriend\\b",
                           "\\binline\\b", "\\bint\\b", "\\blong\\b", "\\bnamespace\\b",
                           "\\boperator\\b", "\\bprivate\\b", "\\bprotected\\b",
                           "\\bpublic\\b", "\\bshort\\b", "\\bsignals\\b", "\\bsigned\\b",
                           "\\bslots\\b", "\\bstatic\\b", "\\bstruct\\b",
                           "\\btemplate\\b", "\\btypedef\\b", "\\btypename\\b",
                           "\\bunion\\b", "\\bunsigned\\b", "\\bvirtual\\b", "\\bvoid\\b",
                           "\\bvolatile\\b"]

        self.highlightingRules = [(QRegExp(pattern), keywordFormat)
                                  for pattern in keywordPatterns]

        classFormat = QTextCharFormat()
        classFormat.setFontWeight(QFont.Bold)
        classFormat.setForeground(Qt.darkMagenta)
        self.highlightingRules.append((QRegExp("\\bབདེ་ལེགས\\b"),
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
        self.highlightingRules.append((QRegExp("\\b[A-Za-z0-9_]+(?=\\()"),
                                       functionFormat))

        self.commentStartExpression = QRegExp("/\\*")
        self.commentEndExpression = QRegExp("\\*/")

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.commentStartExpression.indexIn(text)

        while startIndex >= 0:
            endIndex = self.commentEndExpression.indexIn(text, startIndex)

            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + \
                    self.commentEndExpression.matchedLength()

            self.setFormat(startIndex, commentLength,
                           self.multiLineCommentFormat)
            startIndex = self.commentStartExpression.indexIn(text,
                                                             startIndex + commentLength)
