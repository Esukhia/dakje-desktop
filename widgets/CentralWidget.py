from PyQt5 import QtCore, QtGui, QtWidgets

import pybo

from .Tabs import LevelTab, EditorTab
from .TextEdit import TextEdit
from .CQLWidget import CqlQueryGenerator

class CentralWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.findWidget = FindWidget(self)
        self.textEdit = TextEdit(self)
        self.tabWidget = TabWidget(self)

        self.hbox = QtWidgets.QHBoxLayout(self)
        self.hbox.addWidget(self.findWidget)
        self.hbox.addWidget(self.textEdit)
        self.hbox.addWidget(self.tabWidget)
        self.hbox.setStretch(0, 1)
        self.hbox.setStretch(1, 3)
        self.hbox.setStretch(2, 1)

class FindWidget(QtWidgets.QWidget):
    MODE_SIMPLE = 1
    MODE_CQL = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initForms()
        self.initResult()

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.vbox.addLayout(self.forms)
        self.vbox.addSpacing(50)
        self.vbox.addWidget(self.resultLabel)
        self.vbox.addWidget(self.resultList)

    @property
    def editor(self):
        return self.parent().parent()

    @property
    def textEdit(self):
        return self.editor.textEdit

    def initForms(self):
        self.forms = QtWidgets.QFormLayout()
        self.forms.addRow(QtWidgets.QLabel('Find & Replace'), None)

        # Find Form
        self.findInput = QtWidgets.QLineEdit()
        self.findBtn = QtWidgets.QPushButton('Find')

        self.cqlQueryGenerator = CqlQueryGenerator(self.findInput)
        self.cqlQueryGeneratorBtn = QtWidgets.QPushButton()
        self.cqlQueryGeneratorBtn.setFlat(True)
        self.cqlQueryGeneratorBtn.setIcon(QtGui.QIcon('icons/CQL.png'))
        self.cqlQueryGeneratorBtn.setIconSize(QtCore.QSize(30, 30))
        self.cqlQueryGeneratorBtn.clicked.connect(
            lambda: self.cqlQueryGenerator.show())

        self.findhbox = QtWidgets.QHBoxLayout()
        self.findhbox.addWidget(self.findInput)
        self.findhbox.addWidget(self.cqlQueryGeneratorBtn)
        self.findhbox.addWidget(self.findBtn)
        self.forms.addRow(self.findhbox)

        # Find Mode Choices
        self.mode = self.MODE_SIMPLE
        self.simpleRadio = QtWidgets.QRadioButton('Simple')
        self.simpleRadio.setChecked(True)
        self.cqlRadio = QtWidgets.QRadioButton('CQL')

        self.modeChoiceshbox = QtWidgets.QHBoxLayout()
        self.modeChoiceshbox.addWidget(self.simpleRadio)
        self.modeChoiceshbox.addWidget(self.cqlRadio)
        self.forms.addRow(self.modeChoiceshbox)

        # Replace Form
        self.replaceInput = QtWidgets.QLineEdit()
        self.replaceBtn = QtWidgets.QPushButton('Replace')
        self.replaceAllBtn = QtWidgets.QPushButton('ReplaceAll')
        self.forms.addRow(self.replaceInput, self.replaceBtn)
        self.forms.addRow(None, self.replaceAllBtn)

        # Connected
        self.findBtn.clicked.connect(self._find)
        self.replaceBtn.clicked.connect(self.replace)
        self.replaceAllBtn.clicked.connect(self.replaceAll)

    def initResult(self):
        # Results
        self.resultLabel = QtWidgets.QLabel('Result')
        self.resultList = QtWidgets.QListWidget(self)

        self.resultList.itemClicked.connect(self.itemClicked)

    def _find(self):
        self.resultList.clear()

        if self.simpleRadio.isChecked():
            self.mode = self.MODE_SIMPLE
            self.findText()
        else:  # cqlRadio
            self.mode = self.MODE_CQL
            self.findCqlTokens()

        # click first
        self.clickItem(0)

    def findCqlTokens(self):
        query = self.findInput.text()
        matcher = pybo.CQLMatcher(query)
        tokens = self.editor.tokens

        slices = matcher.match([t.pyboToken for t in tokens])

        for slice in slices:
            item = QtWidgets.QListWidgetItem()
            item.slice = list(slice)
            item.setText(' '.join(
                [w.content for w in tokens[slice[0]:slice[1]+1]]))
            self.resultList.addItem(item)

        self.resultLabel.setText(str(len(slices)) + " Matches")

    def findText(self):
        query = self.findInput.text()
        matchNum = 0

        cursor = self.textEdit.textCursor()
        cursor.setPosition(0)
        self.textEdit.setTextCursor(cursor)

        while self.textEdit.find(query):
            cursor = self.textEdit.textCursor()
            item = QtWidgets.QListWidgetItem()
            item.slice = [cursor.selectionStart(), cursor.selectionEnd()]
            item.setText(cursor.selectedText())
            self.resultList.addItem(item)
            matchNum += 1

        self.resultLabel.setText(str(matchNum) + " Matches")

    def itemClicked(self, item):
        if self.mode == self.MODE_SIMPLE:
            self.textEdit.setSelection(item.slice[0], item.slice[1])
        else:
            self.textEdit.setTokensSelection(item.slice[0], item.slice[1])

    def clickItem(self, row):
        if row < self.resultList.count():
            self.resultList.setCurrentRow(row)
            self.itemClicked(self.resultList.item(row))

    def replace(self):
        if self.editor.viewManager.isPlainTextView():
            cursor = self.textEdit.textCursor()
            if cursor.hasSelection():
                cursor.insertText(self.replaceInput.text())
                self.editor.segment()
                self._find()
        else:
            QtWidgets.QMessageBox.warning(
                self, 'Mode Error',
                'Please replace text in plain text mode.',
                buttons=QtWidgets.QMessageBox.Ok
            )

    def replaceAll(self):
        if self.editor.viewManager.isPlainTextView():
            for _ in range(self.resultList.count()):
                self.clickItem(0)
                self.replace()
        else:
            QtWidgets.QMessageBox.warning(
                self, 'Mode Error',
                'Please replace text in plain text mode.',
                buttons=QtWidgets.QMessageBox.Ok
            )


class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.levelTab = LevelTab(self)
        self.editorTab = EditorTab(self)

        self.addTab(self.levelTab, 'Level Mode')
        self.addTab(self.editorTab, 'Editor Mode')
