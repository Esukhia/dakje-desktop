import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence, QTextDocumentWriter, QFont
from PyQt5.QtWidgets import QMainWindow, QMessageBox, \
    QFileDialog, QAction, QApplication, QMenuBar, QPlainTextEdit, \
    QUndoCommand, QUndoStack, QUndoView


class EmulatedTextUndoCommand(QUndoCommand):

    def __init__(self, edit, oldText, newText,
                 oldCursorPosition=None, newCursorPosition=None):
        super(EmulatedTextUndoCommand, self).__init__("")
        self.edit = edit
        self.oldText = oldText
        self.newText = newText
        self.oldCursorPosition = oldCursorPosition
        self.newCursorPosition = newCursorPosition

        self.called = False

    def redo(self):
        if not self.called:
            self.called = True
            return

        print("redo: %s" % self)
        self.edit._setPlainText(self.newText)
        if self.newCursorPosition:
            print("redo cursor position: %d" % self.newCursorPosition)
            t = self.edit.textCursor()
            t.setPosition(self.newCursorPosition)
            self.edit.setTextCursor(t)

    def undo(self):
        print("undo: %s" % self)
        self.edit._setPlainText(self.oldText)
        if self.oldCursorPosition:
            print("undo cursor position: %d" % self.oldCursorPosition)
            t = self.edit.textCursor()
            t.setPosition(self.oldCursorPosition)
            self.edit.setTextCursor(t)

    def __str__(self, *args, **kwargs):
        return "old: %s, new: %s" % (self.oldText, self.newText)

class CustomUndoTextEdit(QPlainTextEdit):
    def __init__(self, *args, undoStack=None, **kws):
        super().__init__(*args, **kws)

        self.undoStack = (undoStack if undoStack is not None
                          else QUndoStack(self))
        self.textChangedAfterUndoCommandAdded = False

        self.document().undoCommandAdded.connect(
            self.onUndoCommandAdded)
        self.textChanged.connect(self.onTextChanged)

    def _setPlainText(self, text):
        return QPlainTextEdit.setPlainText(self, text)

    def setPlainText(self, text):
        command = EmulatedTextUndoCommand(self,
            self.toPlainText(), text,
                self.textCursor().position(),
                self.textCursor().position())
        self.undoStack.push(command)

        result = QPlainTextEdit.setPlainText(self, text)
        self.textChangedAfterUndoCommandAdded = False
        return result

    def keyPressEvent(self, event):
        print("keyPressEvent")
        if event.key() == (Qt.Key_Control and Qt.Key_Z):
            print("press Undo")
            self.undo()
        elif event.key() == (Qt.Key_Control and Qt.Key_Y):
            print("press Redo")
            self.redo()
        else: # call base class keyPressEvent
            QPlainTextEdit.keyPressEvent(self, event)

    def onTextChanged(self):
        print("onTextChanged")
        self.textChangedAfterUndoCommandAdded = True

    def onUndoCommandAdded(self):
        print("insert undo command: %s %d" % (
            self.toPlainText(), self.textCursor().position()))
        if self.undoStack.isClean():
            command = EmulatedTextUndoCommand(
                self, "", self.toPlainText(),
                None, self.textCursor().position())
        else:
            lastCommand = self.undoStack.command(self.undoStack.count() - 1)
            command = EmulatedTextUndoCommand(
                self, lastCommand.newText, self.toPlainText(),
                lastCommand.newCursorPosition,
                self.textCursor().position())
        self.undoStack.push(command)
        self.textChangedAfterUndoCommandAdded = False

    def undo(self):
        print("undo")
        if self.textChangedAfterUndoCommandAdded:
            lastCommand = self.undoStack.command(self.undoStack.count() - 1)
            command = EmulatedTextUndoCommand(
                self, lastCommand.newText, self.toPlainText(),
                lastCommand.newCursorPosition,
                self.textCursor().position())
            self.undoStack.push(command)

        self.undoStack.undo()
        self.textChangedAfterUndoCommandAdded = False

    def redo(self):
        print("redo")
        self.undoStack.redo()
        self.textChangedAfterUndoCommandAdded = False


class MyUndoStack(QUndoStack):
    def undo(self, *args, **kwargs):
        print("MyUndoStack: undo")
        return QUndoStack.undo(self, *args, **kwargs)


class BasicEditor(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.undoStack = QUndoStack(self)

        self.setupTextEdit()
        self.createActions()

        self.initUI()

        self.filename = None


    def initUI(self):
        self.setupMenus()
        self.setupToolBar()
        self.setupLayout()

        self.setWindowTitle("Untitled - Editor")
        self.setWindowIcon(QIcon("tab1.png"))
        self.setWindowState(Qt.WindowMaximized)
        self.resize(1200, 480)

    def setupTextEdit(self):
        font = QFont()
        # font.setFamily('Noto Sans Tibetan')
        font.setFixedPitch(True)
        font.setPointSize(15)

        self.textEdit = CustomUndoTextEdit(undoStack=self.undoStack)
        self.textEdit.setFont(font)

        #self.textEdit.redoAvailable.connect(self.redoAction.setEnabled)
        #self.textEdit.undoAvailable.connect(self.undoAction.setEnabled)

    def setupMenus(self):
        self.menu = self.menuBar()

        # File
        fileMenu = self.menu.addMenu("&File")
        fileMenu.addAction(self.newFileAction)
        fileMenu.addAction(self.openFileAction)
        fileMenu.addAction(self.saveFileAction)
        fileMenu.addAction(self.actionQuit)

        # Edit
        editMenu = self.menu.addMenu("&Edit")
        editMenu.addAction(self.undoAction)
        editMenu.addAction(self.redoAction)

        # Settings
        helpMenu = self.menu.addMenu("&Help")
        helpMenu.addAction("About &Qt", QApplication.instance().aboutQt)

        self.menuBarRight = QMenuBar(self.menu)
        self.menu.setCornerWidget(self.menuBarRight, Qt.TopRightCorner)

    def setupToolBar(self):
        self.toolbar = self.addToolBar("toolbar")
        self.toolbar.addAction(self.newFileAction)
        self.toolbar.addAction(self.openFileAction)
        self.toolbar.addAction(self.saveFileAction)

        self.toolbar.addSeparator()
        self.toolbar.addAction(self.undoAction)
        self.toolbar.addAction(self.redoAction)

    def setupLayout(self):
        self.setCentralWidget(self.textEdit)

    def createActions(self, BASE_DIRECTORY='.'):

        ### New File ###
        self.newFileAction = QAction(
            QIcon(os.path.join(BASE_DIRECTORY, 'icons/new.png')),
            "&New...", self, )
        self.newFileAction.setShortcut(QKeySequence.New)
        self.newFileAction.setStatusTip("Create a new file")
        self.newFileAction.triggered.connect(self.newFile)

        ### Open File ###
        self.openFileAction = QAction(
            QIcon(os.path.join(BASE_DIRECTORY, 'icons/open.png')),
            "&Open...", self)
        self.openFileAction.setShortcut(QKeySequence.Open)
        self.openFileAction.setStatusTip("Open a text file")
        self.openFileAction.triggered.connect(self.openFile)

        ### Save File ###
        self.saveFileAction = QAction(
            QIcon(os.path.join(BASE_DIRECTORY, 'icons/save.png')),
            "&Save...", self, )
        self.saveFileAction.setShortcut(QKeySequence.Save)
        self.saveFileAction.setStatusTip("Save the current document")
        self.saveFileAction.triggered.connect(self.saveFile)

        ### Undo ###
        self.undoAction = QAction(
            QIcon(os.path.join(BASE_DIRECTORY, 'icons/undo.png')),
            "&Undo", self)
#         self._undoAction = self.undoStack.createUndoAction(self, "&Undo")
#         self._undoAction.setIcon(QIcon(os.path.join(
#             BASE_DIRECTORY, 'icons/undo.png')));
        self.undoAction.setShortcut(QKeySequence.Undo)
        self.undoAction.setStatusTip("Undo the last editing action")
        self.undoAction.setEnabled(False)
        self.undoAction.triggered.connect(self.textEdit.undo)
        self.undoStack.canUndoChanged.connect(self.undoAction.setEnabled)

        ### Redo ###
        self.redoAction = QAction(
            QIcon(os.path.join(BASE_DIRECTORY, 'icons/redo.png')),
            "&Redo", self)
#         self.redoAction = self.undoStack.createRedoAction(self, "&Redo")
#         self.redoAction.setIcon(QIcon(os.path.join(
#             BASE_DIRECTORY, 'icons/redo.png')));
        self.redoAction.setShortcut(QKeySequence.Redo)
        self.redoAction.setStatusTip("Redo the last editing action")
        self.redoAction.setEnabled(False)
        self.redoAction.triggered.connect(self.textEdit.redo)
        self.undoStack.canRedoChanged.connect(self.redoAction.setEnabled)

        ### Quit ###
        self.actionQuit = QAction("&Quit", self)
        self.actionQuit.setShortcut(QKeySequence.Open)
        self.actionQuit.setStatusTip("Ctrl+Q")
        self.actionQuit.triggered.connect(self.close)

    def about(self):
        QMessageBox.about(self, "About PyTib Editor",
                          "rules using regular expressions.</p>")

    def newFile(self):
        self.textEdit.clear()

    def openFile(self):
        self.filename, ok = QFileDialog.getOpenFileName(
            self, 'Open File', ".", "UTF-8 (*.txt)")

        if self.filename:
            with open(self.filename, "r", encoding='utf-8') as f:
                self.textEdit.setPlainText(f.read())

    def saveFile(self):
        self.textEdit.setPlainText("segmented text")
        return

        if not self.filename:
            self.filename, ok = QFileDialog.getSaveFileName(
                self, "Choose a file name", '.', "UTF-8 (*.txt)")

            if not ok:
                return

        if not self.filename:
            return

        self.statusBar().showMessage("Saved '%s'" % self.filename, 2000)

        writer = QTextDocumentWriter(self.filename)
        success = writer.write(self.textEdit.document())

        if not success:
            QMessageBox.question(self, 'Cancel', 'Saving Failed',
                                 QMessageBox.Yes)
            return


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BasicEditor()
    window.show()

    try:
        sys.exit(app.exec_())
    except:
        print("exiting")
        sys.exit(1)
