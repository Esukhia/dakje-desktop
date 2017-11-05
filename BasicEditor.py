
import sys

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QFile
from PyQt5.QtGui import QIcon, QKeySequence, QTextDocumentWriter, QFont
from PyQt5.QtWidgets import QMainWindow, QWidget, QMessageBox, \
    QFileDialog, QAction, QTextEdit, QVBoxLayout, QHBoxLayout, QApplication, QMenuBar, QPlainTextEdit

class BasicEditor(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.createActions()
        self.setupTextEdit()
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

        self.textEdit = QTextEdit()
        self.textEdit.setFont(font)

        self.textEdit.redoAvailable.connect(self.redoAction.setEnabled)
        self.textEdit.undoAvailable.connect(self.undoAction.setEnabled)

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

    def createActions(self):
        ### New File ###
        self.newFileAction = QAction(
            QIcon('files/filenew.png'), "&New...", self,)
        self.newFileAction.setShortcut(QKeySequence.New)
        self.newFileAction.setStatusTip("Create a new file")
        self.newFileAction.triggered.connect(self.newFile)

        ### Open File ###
        self.openFileAction = QAction(
            QIcon('files/fileopen.png'), "&Open...", self)
        self.openFileAction.setShortcut(QKeySequence.Open)
        self.openFileAction.setStatusTip("Open a text file")
        self.openFileAction.triggered.connect(self.openFile)

        ### Save File ###
        self.saveFileAction = QAction(
            QIcon('files/filesave.png'), "&Save...", self,)
        self.saveFileAction.setShortcut(QKeySequence.Save)
        self.saveFileAction.setStatusTip("Save the current document")
        self.saveFileAction.triggered.connect(self.saveFile)

        ### Undo ###
        self.undoAction = QAction(
            QIcon('files/editundo.png'), "&Undo", self)
        self.undoAction.setShortcut(QKeySequence.Undo)
        self.undoAction.setStatusTip("Undo the last editing action")
        self.undoAction.triggered.connect(self.undo)

        ### Redo ###
        self.redoAction = QAction(
            QIcon('files/editredo.png'), "&Redo", self)
        self.redoAction.setShortcut(QKeySequence.Redo)
        self.redoAction.setStatusTip("Redo the last editing action")
        self.redoAction.triggered.connect(self.redo)

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
                self.textEdit.setText(f.read())


    def saveFile(self):
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

    def undo(self):
        self.textEdit.document().undo()

    def redo(self):
        self.textEdit.document().redo()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BasicEditor()
    window.show()

    try:
        sys.exit(app.exec_())
    except:
        print("exiting")
        sys.exit(1)
