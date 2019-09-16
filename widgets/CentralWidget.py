from PyQt5 import QtCore, QtGui, QtWidgets

import os
import botok

from .Tabs import LevelTab, EditorTab, FindTab, CorpusAnalysisTab
from .TextEdit import TextEdit

from web.settings import BASE_DIR

class CentralWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.leftTabWidget = LeftTabWidget(self)
        self.textEdit = TextEdit(self)
        self.tabWidget = TabWidget(self)

        self.hbox = QtWidgets.QHBoxLayout(self)
        self.hbox.addWidget(self.leftTabWidget)
        self.hbox.addWidget(self.textEdit)
        self.hbox.addWidget(self.tabWidget)
        self.hbox.setStretch(0, 1)
        self.hbox.setStretch(1, 3)
        self.hbox.setStretch(2, 1)


class LeftTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.findTab = FindTab(self)
        self.corpusAnalysisTab = CorpusAnalysisTab(self)

        self.addTab(self.findTab, 'Find and Replace')
        self.addTab(self.corpusAnalysisTab, 'Corpus Analysis')

        self.currentChanged.connect(self.tabChanged)
        

    @property
    def editor(self):
        return self.parent().parent()

    def tabChanged(self):
        if self.currentIndex() == 0:
            self.editor.mode = 'Find and Replace'
        else:
            self.editor.mode = 'Level Mode'
        self.editor.showStatus()

class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.levelTab = LevelTab(self)
        self.editorTab = EditorTab(self)

        self.addTab(self.levelTab, 'Level Mode')
        self.addTab(self.editorTab, 'Editor Mode')

        self.currentChanged.connect(self.tabChanged)

    @property
    def editor(self):
        return self.parent().parent()

    def tabChanged(self):
        if self.currentIndex() == 0:
            self.editor.mode = 'Level Mode'
        else:
            self.editor.mode = 'Editor Mode'
        self.editor.showStatus()
