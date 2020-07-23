from PyQt5 import QtWidgets

from .Tabs import LevelTab, FindTab, CorpusAnalysisTab, EditorTab
from .TextEdit import TextEdit
from django.utils.translation import gettext_lazy as _

class CentralWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # create widget object of the window
        self.leftTabWidget = LeftTabWidget(self)
        self.textEdit = TextEdit(self, undoStack=parent.undoStack)
        self.tabWidget = TabWidget(self)
        # arrange in order horizontally (from left to right)
        self.hbox = QtWidgets.QHBoxLayout(self)
        self.hbox.addWidget(self.leftTabWidget)
        self.hbox.addWidget(self.textEdit)
        self.hbox.addWidget(self.tabWidget)
        self.hbox.setStretch(0, 1)
        self.hbox.setStretch(1, 3)
        self.hbox.setStretch(2, 1)

# left part of the window
class LeftTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.findTab = FindTab(self)
        # create Corpus object of the window
        self.corpusAnalysisTab = CorpusAnalysisTab(self)
        self.addTab(self.corpusAnalysisTab, str(_('Corpus')))
        # FNR tab:
        # self.addTab(self.findTab, 'Find and Replace')
        # self.currentChanged.connect(self.tabChanged)

    @property
    def editor(self):
        return self.parent().parent()

    def tabChanged(self):
        if self.currentIndex() == 0:
            self.editor.mode = str(_('Find and Replace'))
        else:
            self.editor.mode = 'གསལ་ཆ།'
        self.editor.showStatus()

# right part of the window
class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFont(self.editor.uiFont)

        # self.editorTab = EditorTab(self)
        self.levelTab = LevelTab(self)

        # self.addTab(self.editorTab, 'ཞུ་དག')
        self.addTab(self.levelTab, 'གསལ་ཆ།')# Level Mode
        # when currentChanged call the method of tabChanged
        self.currentChanged.connect(self.tabChanged)

    @property
    def editor(self):
        return self.parent().parent()

    # show Level Mode or Editor Mode
    def tabChanged(self):
        if self.currentIndex() == 0:
            self.editor.mode = 'གསལ་ཆ།'
        else:
            self.editor.mode = 'ཞུ་དག'
        self.editor.showStatus()
