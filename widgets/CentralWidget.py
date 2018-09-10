from PyQt5 import QtCore, QtGui, QtWidgets

from .Tabs import LevelTab, EditorTab
from .TextEdit import TextEdit

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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initForms()
        self.initResult()

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.vbox.addLayout(self.forms)
        self.vbox.addSpacing(50)
        self.vbox.addWidget(self.resultLabel)
        self.vbox.addWidget(self.resultList)

    def initForms(self):
        self.forms = QtWidgets.QFormLayout()
        self.forms.addRow(QtWidgets.QLabel('Find & Replace'), None)

        # Find Form
        self.findInput = QtWidgets.QLineEdit()
        self.findBtn = QtWidgets.QPushButton('Find')
        self.forms.addRow(self.findInput, self.findBtn)

        # Find Mode Choices
        self.simpleRadio = QtWidgets.QRadioButton('Simple')
        self.cqlRadio = QtWidgets.QRadioButton('CQL')
        self.forms.addRow(self.simpleRadio, self.cqlRadio)

        # Replace Form
        self.replaceInput = QtWidgets.QLineEdit()
        self.replaceBtn = QtWidgets.QPushButton('Replace')
        self.replaceAllBtn = QtWidgets.QPushButton('ReplaceAll')
        self.forms.addRow(self.replaceInput, self.replaceBtn)
        self.forms.addRow(None, self.replaceAllBtn)

    def initResult(self):
        # Results
        self.resultLabel = QtWidgets.QLabel('Result')
        self.resultList = QtWidgets.QListWidget(self)
        self.resultList.addItem('Result1')
        self.resultList.addItem('Result2')
        self.resultList.addItem('Result3')
        self.resultList.addItem('Result4')


class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.levelTab = LevelTab(self)
        self.editorTab = EditorTab(self)

        self.addTab(self.levelTab, 'Level Mode')
        self.addTab(self.editorTab, 'Editor Mode')
