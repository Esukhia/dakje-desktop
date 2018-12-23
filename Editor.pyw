import os
import sys

from functools import partial
from collections import Counter

import Configure

Configure.configure()

from PyQt5 import QtCore, QtWidgets, QtGui
from pybo import CQLMatcher

from widgets import MenuBar, ToolBar, CentralWidget, EditTokenDialog, Highlighter
from managers import ActionManager, TokenManager, ViewManager, FormatManager


class ExceptionHandler(QtCore.QObject):
    errorSignal = QtCore.pyqtSignal()

    def __init__(self):
        super(ExceptionHandler, self).__init__()

    def handler(self, exctype, value, traceback):
        self.errorSignal.emit()
        sys._excepthook(exctype, value, traceback)

exceptionHandler = ExceptionHandler()
sys._excepthook = sys.excepthook
sys.excepthook = exceptionHandler.handler


class Editor(QtWidgets.QMainWindow):
    BASE_DIR = os.path.dirname(__name__)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initProperties()
        self.initManagers()
        self.initUI()
        self.bindEvents()
        self.setWindowTitle("Tibetan Editor")
        self.setWindowState(QtCore.Qt.WindowMaximized)

        self.textEdit.setPlainText = self.ignoreCursorPositionChanged(
            self.textEdit.setPlainText)

    def ignoreEvent(self, func, signal, event):
        def _func(*arg, **kwargs):
            signal.disconnect()
            func(*arg, **kwargs)
            signal.connect(event)
        return _func

    def ignoreCursorPositionChanged(self, func):
        return self.ignoreEvent(func,
                                self.textEdit.cursorPositionChanged,
                                self.cursorPositionChanged)

    def initProperties(self):
        self.tokens = []
        self.formats = []
        self.mode = None  # LEVEL_MODE, EDITOR_MODE
        self.view = None  # PLAIN_TEXT_VIEW, SPACE_VIEW...
        self.filename = None

        self.editTokenDialog = EditTokenDialog(self)

    def initManagers(self):
        self.actionManager = ActionManager(self)
        self.tokenManager = TokenManager(self)
        self.viewManager = ViewManager(self)
        self.formatManager = FormatManager(self)

    def initUI(self):
        self.actionManager.createActions()

        self.menuBar = MenuBar(self.actionManager, parent=self)
        self.setMenuBar(self.menuBar)

        self.toolBar = ToolBar(self.actionManager, parent=self)
        self.addToolBar(self.toolBar)

        self.statusBar = QtWidgets.QStatusBar(parent=self)
        self.setStatusBar(self.statusBar)
        self.statusBar.setStyleSheet('background-color: #EAEAEA')
        self.statusBar.showMessage('Welcome...', 3000)

        self.centralWidget = CentralWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.highlighter = Highlighter(self.textEdit.document(), self)

        self.setStyleSheet('QMainWindow{background-color: white}')
        self.textEdit.setStyleSheet(
            'border: none; font-size: 20px; margin: 10px;')

    def bindEvents(self):
        self.bindCursorPositionChanged()
        self.bindLevelButtons()

    def bindCursorPositionChanged(self):
        self.textEdit.cursorPositionChanged.connect(self.cursorPositionChanged)

    def bindLevelButtons(self):
        self.levelTab.level1Button.clicked.connect(
            # partial(self.importRuleList, level=1)
            partial(self.importLevelList, level=1)
        )

        self.levelTab.level2Button.clicked.connect(
            partial(self.importLevelList, level=2))

        self.levelTab.level3Button.clicked.connect(
            partial(self.importLevelList, level=3))

    # Tool Bar Actions #

    def toggleSpaceView(self):
        self.segment()
        self.viewManager.toggleSpaceView()
        self.refreshView()

    def toggleTagView(self):
        self.segment()
        self.viewManager.toggleTagView()
        self.refreshView()

    def segment(self):
        if self.tokens:
            return
        text = self.centralWidget.textEdit.toPlainText()
        tokens = self.tokenManager.segment(text)
        self.tokens.extend(tokens)

    # TextEdit #

    @property
    def textEdit(self):
        return self.centralWidget.textEdit

    @property
    def levelTab(self):
        return self.centralWidget.tabWidget.levelTab

    # TextEdit Actions #

    def newFile(self):
        self.textEdit.newFile()

    def openFile(self):
        self.textEdit.openFile()
        self.segment()
        self.refreshView()

    def saveFile(self):
        self.filename = self.textEdit.saveFile()

    def undo(self):
        self.textEdit.undo()

    def redo(self):
        self.textEdit.redo()

    # TextEdit Events #

    def cursorPositionChanged(self):
        position = self.textEdit.textCursor().position()

        if (self.viewManager.isTagView() and
                not self.editTokenDialog.isVisible()):
            token = self.tokenManager.find(position)
            self.editTokenDialog.setToken(token)
            self.editTokenDialog.show()

    # Level List #

    def importLevelList(self, level):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self)

        with open(filePath, encoding='utf-8') as f:
            words = [word[:-1] if word.endswith('་') else word
                     for word in [line.rstrip('\r\n')
                                  for line in f.readlines()]]

        for token in self.tokens:
            if token.contentWithoutTsek in words:
                token.level = level

        self.refreshView()
        self.refreshCoverage()

    def importRuleList(self, level):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self)

        with open(filePath, encoding='utf-8') as f:
            rules = [line.rstrip('\r\n') for line in f.readlines()]

        for rule in rules:
            matcher = CQLMatcher(rule)
            slices = matcher.match([t.pyboToken for t in self.tokens])

            for slice in slices:
                for token in self.tokens[slice[0]:slice[1] + 1]:
                    token.level = level

        self.refreshView()
        self.refreshCoverage()

    # Refresh #

    def refreshView(self):
        text = self.tokenManager.getString()
        self.textEdit.setPlainText(text)

    def refreshCoverage(self):
        counter = Counter([token.level for token in self.tokens])

        def getProp(key):
            return counter[key] / len(self.tokens) * 100.0

        self.levelTab.tokenCoverageProgBar.setValue(100 - getProp(None))
        self.levelTab.levelNoneProgBar.setValue(getProp(None))
        self.levelTab.level1ProgBar.setValue(getProp(1))
        self.levelTab.level2ProgBar.setValue(getProp(2))
        self.levelTab.level3ProgBar.setValue(getProp(3))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Editor()
    window.show()

    from django.core.management import call_command

    import multiprocessing

    multiprocessing.Process(target=call_command, args=('runserver',)).start()

    try:
        sys.exit(app.exec_())
    except:
        print("exiting")
        sys.exit(1)
