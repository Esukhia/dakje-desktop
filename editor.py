#!/usr/local/bin/env python3.5
# -*- coding: utf-8 -*-

import sys

import PyQt5
from PyQt5.QtCore import QFile, QRegExp, Qt, QTextStream
from PyQt5.QtGui import (QFont, QIcon, QKeySequence, QPixmap,
                         QSyntaxHighlighter, QTextCharFormat, QTextCursor,
                         QTextTableFormat)
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QDialog,
                             QDockWidget, QFileDialog, QGridLayout, QLabel,
                             QLineEdit, QListView, QListWidget,
                             QListWidgetItem, QMainWindow, QMenu, QMenuBar,
                             QMessageBox, QPushButton, QRadioButton,
                             QStyleFactory, QTableView, QTextEdit, QWidget)

import highlighter


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

# Editor
    def setupEditor(self):
        font = QFont()
        font.setFamily('Noto Sans Tibetan')
        font.setFixedPitch(True)
        font.setPointSize(15)

        self.editor = QTextEdit()
        self.editor.setFont(font)

        self.highlighter = highlighter.Highlighter(
            self.editor.document(), self.levelLists)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def createToolbar(self):
        self.toolbar = self.addToolBar("toolbar")
        self.toolbar.addAction(self.newFileAction)
        self.toolbar.addAction(self.openFileAction)
        self.toolbar.addAction(self.saveFileAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.undoAction)
        self.toolbar.addAction(self.redoAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.segmentAction)

    def createMenus(self):
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
        editMenu.addAction("About &Qt", QApplication.instance().aboutQt)
        # Tools
        self.viewMenu = self.menu.addMenu("&View")
        self.viewMenu.addAction(self.segmentAction)
        self.viewMenu.addAction(
            "&Spellchecker", QApplication.instance().aboutQt)
        self.viewMenu.addAction("&Highlighter", self.about)
        # Settings
        settingsMenu = self.menu.addMenu("&Help")
        settingsMenu.addAction("&Highlighter", self.about)

        self.menuBarRight = QMenuBar(self.menu)
        self.menu.setCornerWidget(self.menuBarRight, Qt.TopRightCorner)

    def initUI(self):
        self.createActions()
        self.createMenus()
        self.createToolbar()
        self.loadLists()
        self.setupEditor()
        self.createStatusBar()
        self.setCentralWidget(self.editor)
        self.setWindowTitle("Tibetan Editor")
        self.setWindowIcon(QIcon("tab1.png"))
        self.setWindowState(Qt.WindowMaximized)
        self.resize(1200, 480)

# Actions
    def about(self):
        QMessageBox.about(self, "About PyTib Editor",
                          "rules using regular expressions.</p>")

    def newFile(self):
        self.editor.clear()

    def openFile(self, path=None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "Open File", '',
                                                  "UTF-8 files (*.txt)")

        if path:
            inFile = QFile(path)
            if inFile.open(QFile.ReadOnly | QFile.Text):
                text = inFile.readAll()

                try:
                    text = str(text, encoding="UTF-8")
                    print("try")
                except:
                    print("except")
                self.editor.setPlainText(text)

    def saveFile(self):
        filename, _ = QFileDialog.getSaveFileName(self,
                                                  "Choose a file name", '.', "UTF-8 (*.txt)")
        if not filename:
            return

        file = QFile(filename)
        if not file.open(QFile.WriteOnly | QFile.Text):
            QMessageBox.warning(self, "Dock Widgets",
                                "Cannot write file %s:\n%s." % (filename, file.errorString()))
            return

        out = QTextStream(file)
        out.setCodec("UTF-8")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        out << self.editor.toPlainText()
        QApplication.restoreOverrideCursor()

        self.statusBar().showMessage("Saved '%s'" % filename, 2000)

    def undo(self):
        document = self.editor.document()
        document.undo()

    def redo(self):
        document = self.editor.document()
        document.redo()

    def segment(self):
        self.statusBar().showMessage("Segment")

    def createActions(self):
        self.newFileAction = QAction(QIcon('files/filenew.png'), "&New...",
                                     self, shortcut=QKeySequence.New,
                                     statusTip="Create a new file", triggered=self.newFile)
        self.openFileAction = QAction(QIcon('files/fileopen.png'), "&Open...",
                                      self, shortcut=QKeySequence.Open,
                                      statusTip="Open a text file", triggered=self.openFile)
        self.saveFileAction = QAction(QIcon('files/filesave.png'), "&Save...", self,
                                      shortcut=QKeySequence.Save,
                                      statusTip="Save the current document", triggered=self.saveFile)
        self.undoAction = QAction(QIcon('files/editundo.png'), "&Undo", self,
                                  shortcut=QKeySequence.Undo,
                                  statusTip="Undo the last editing action", triggered=self.undo)
        self.redoAction = QAction(QIcon('files/editredo.png'), "&Redo", self,
                                  shortcut=QKeySequence.Redo,
                                  statusTip="Redo the last editing action", triggered=self.redo)
        self.segmentAction = QAction(QIcon('files/segment.png'), "&Segment", self,
                                     shortcut="Ctrl+Shift+C",
                                     statusTip="Segment the current document", triggered=self.segment)
        self.actionQuit = QAction("&Quit", self, shortcut="Ctrl+Q",
                                  triggered=self.close)

# Get Lists
# TODO: get the level files in the Levels folder, read their names,
# convert their content into a list of regexes and create a dict for
# highlighter.py. A spaces should be added before and after each list
# entry so they can only be discovered after segmentation.

    def loadLists(self):
        self.levelLists = {'Level1': ['ya', 'yo']}
        return self.levelLists

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
