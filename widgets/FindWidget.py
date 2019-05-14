from functools import partial

from pybo import CQLMatcher, TokenSplit

from PyQt5.QtCore import Qt, QStringListModel, QSize
from PyQt5.QtGui import QTextCursor, QPalette, QIcon, QTextDocument
from PyQt5.QtWidgets import (
    QWidget, QTextEdit, QCompleter, QComboBox, QPushButton,
    QLabel, QLineEdit, QFormLayout, QHBoxLayout, QVBoxLayout,

    QListWidget, QListWidgetItem, QCheckBox
)

from collections import OrderedDict

from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import (
    QWidget, QTextEdit, QCompleter, QComboBox, QPushButton,
    QLabel, QLineEdit, QFormLayout
)

from .CQLWidget import CQLQueryGenerator

class FindWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.mode = 'text'
        self.initUI()

    def initUI(self):
        fbox = QFormLayout()

        fbox.addRow(QLabel('Find'))

        self.lineEdit = QLineEdit()
        fbox.addRow(self.lineEdit)
        self.CQLQueryGenerator = CQLQueryGenerator(self.lineEdit)

        self.checkBox = QCheckBox()
        self.checkBox.setText('Using CQL')
        fbox.addRow(self.checkBox)

        button = QPushButton('CQL Generator')
        button.clicked.connect(lambda: self.CQLQueryGenerator.show())
        fbox.addRow(button)

        findBtn = QPushButton('Find')
        findBtn.clicked.connect(self.find)
        fbox.addRow(findBtn)

        self.lineEdit2 = QLineEdit()

        fbox.addRow(QLabel('Replace'))
        fbox.addRow(self.lineEdit2)

        self.replaceButton = QPushButton('Replace')
        self.replaceButton.clicked.connect(self.replaceText)
        self.replaceAllButton = QPushButton('Replace All')
        self.replaceAllButton.clicked.connect(self.replaceAll)
        hbox = QHBoxLayout()
        hbox.addWidget(self.replaceButton)
        hbox.addWidget(self.replaceAllButton)
        fbox.addRow(hbox)

        self.matchesLabel = QLabel('Matches')
        fbox.addRow(self.matchesLabel)

        self.listWidget = QListWidget()
        self.listWidget.itemClicked.connect(self.itemClicked)
        fbox.addRow(self.listWidget)

        self.setLayout(fbox)

    def find(self):
        self.listWidget.clear()

        if self.checkBox.isChecked():
            self.mode = 'cql'
            self.findWords()
        else:
            self.mode = 'text'
            self.findText()

        # click first
        self.clickItem(0)

    def findWords(self):
        query = self.lineEdit.text()
        matcher = CQLMatcher(query)

        words = self.parent.wordManager.getWords()
        slices = matcher.match(
            [w.token for w in words])

        for slice in slices:
            item = QListWidgetItem()
            item.slice = list(slice)
            item.setText(' '.join(
                [w.content for w in words[slice[0]:slice[1]+1]]))
            self.listWidget.addItem(item)

        self.matchesLabel.setText(str(len(slices)) + " Matches")

    def findText(self):
        query = self.lineEdit.text()
        matchNum = 0

        cursor = self.parent.textEdit.textCursor()
        cursor.setPosition(0)
        self.parent.textEdit.setTextCursor(cursor)

        while self.parent.textEdit.find(query):
            cursor = self.parent.textEdit.textCursor()
            item = QListWidgetItem()
            item.slice = [cursor.selectionStart(), cursor.selectionEnd()]
            item.setText(cursor.selectedText())
            self.listWidget.addItem(item)
            matchNum += 1

        self.matchesLabel.setText(str(matchNum) + " Matches")

    def replaceText(self):
        text = self.lineEdit2.text()

        self.parent.textEdit.textCursor().insertText(text)

        item = self.listWidget.currentItem()
        row = self.listWidget.row(item)

        # new word's length minus old word's length
        if self.mode == 'text':
            shift = len(text) - (item.slice[1] - item.slice[0])
        else:  # cql
            shift = -(item.slice[1] - item.slice[0] + 1)

        for i in range(row + 1, self.listWidget.count()):
            item = self.listWidget.item(i)
            item.slice[0] += shift
            item.slice[1] += shift

        self.listWidget.takeItem(row)
        if row < self.listWidget.count():
            self.clickItem(row)

    def replaceAll(self):
        self.find()
        for i in reversed(range(self.listWidget.count())):
            try:
                self.clickItem(i)
                self.replaceText()
            except IndexError:
                # FIXME
                # if the matches have the same indexes,
                # some match will not find the replaced indexes
                # for example: the matches [9, 10], [10, 11]
                # [9, 10] was replaced, [10, 11] will not find the 10th word
                self.listWidget.takeItem(i)

    def itemClicked(self, item):
        if self.mode == 'cql':
            self.parent.selectWord(item.slice[0], item.slice[1])
        else:
            self.parent.setSelection(item.slice[0], item.slice[1])

    def clickItem(self, row):
        if row < self.listWidget.count():
            self.listWidget.setCurrentRow(row)
            self.itemClicked(self.listWidget.item(row))
