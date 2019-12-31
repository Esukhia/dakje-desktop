from PyQt5 import QtWidgets

from .Tabs import LevelTab, FindTab, CorpusAnalysisTab, EditorTab
from .TextEdit import TextEdit

class CentralWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.leftTabWidget = LeftTabWidget(self)
        self.textEdit = TextEdit(self, undoStack=parent.undoStack)
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
        self.addTab(self.corpusAnalysisTab, 'Corpus')
        # FNR tab:
        # self.addTab(self.findTab, 'Find and Replace')
        # self.currentChanged.connect(self.tabChanged)

    @property
    def editor(self):
        return self.parent().parent()

    def tabChanged(self):
        if self.currentIndex() == 0:
            self.editor.mode = 'Find and Replace'
        else:
            self.editor.mode = 'གསལ་ཆ།'
        self.editor.showStatus()

class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFont(self.editor.uiFont)

        # self.editorTab = EditorTab(self)
        self.levelTab = LevelTab(self)

        # self.addTab(self.editorTab, 'ཞུ་དག')
        self.addTab(self.levelTab, 'གསལ་ཆ།')

        self.currentChanged.connect(self.tabChanged)

    @property
    def editor(self):
        return self.parent().parent()

    def tabChanged(self):
        if self.currentIndex() == 0:
            self.editor.mode = 'གསལ་ཆ།'
        else:
            self.editor.mode = 'ཞུ་དག'
        self.editor.showStatus()
