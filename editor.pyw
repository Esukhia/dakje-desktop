#!/usr/local/bin/env python3.5
# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtCore
from PyQt5.QtCore import QFile, Qt
from PyQt5.QtGui import QFont, QIcon, QKeySequence, QTextDocumentWriter, QCursor, QTextCursor
from PyQt5.QtWidgets import (
    QAction, QApplication, QFormLayout, QFileDialog, QGridLayout, QLabel, QListView,
    QColorDialog, QMainWindow, QMenuBar, QMessageBox, QPushButton, QComboBox, QMenu,
    QInputDialog, QStyleFactory, QTextEdit, QWidget, QAbstractItemView, QStyledItemDelegate)

from highlighter import Highlighter
from Word import Word, WordManager

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


def handleException():
    print("ERROR ERROR ERROR")


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.spacesModeOn = False
        self.tagsModeOn = False
        self.textChanged = False
        self.filename = None
        self.firstTextChanged = True
        self.firstSegment = True

        self.tempWords = []
        self.words = []
        self.wordManager = WordManager()
        self.partOfSpeeches = self.wordManager.getPartOfSpeeches()

        self.initUI()

        self.setWindowTitle("Tibetan Editor")
        self.setWindowIcon(QIcon("tab1.png"))
        self.setWindowState(Qt.WindowMaximized)
        self.resize(1200, 480)

        # set button context menu policy
        self.editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.popMenu = self.editor.createStandardContextMenu()
        self.editor.customContextMenuRequested.connect(self.on_context_menu)
        self.popMenu.addAction(self.changeTagAction)

    def initUI(self):
        self.setupEditor()
        self.setupRightBar()
        self.setupColorChangeWidget()
        self.createActions()
        self.createMenus()
        self.createToolbar()
        self.createStatusBar()

        widget = QWidget()
        grid = QGridLayout()
        grid.addWidget(self.editor, 1, 1, 2, 4)
        grid.addWidget(self.changeColorWidget, 1, 5, 1, 1)
        grid.addWidget(self.wordCountWidget, 2, 5, 1, 1)
        widget.setLayout(grid)
        self.setCentralWidget(widget)

    def on_context_menu(self, point):
        # show context menu
        self.popMenu.exec_(self.editor.mapToGlobal(point))

    def setupEditor(self):
        font = QFont()
        # font.setFamily('Noto Sans Tibetan')
        font.setFixedPitch(True)
        font.setPointSize(15)

        self.editor = QTextEdit()
        self.editor.setFont(font)
        self.editor.cursorPositionChanged.connect(self.cursorIsChanged)
        self.editor.textChanged.connect(self.textIsChanged)

        self.highlighter = Highlighter(
            self.editor.document(), editor=self.editor)

    def cursorIsChanged(self):
        self.cursorPosition()

        if self.tagsModeOn:
            position = self.editor.textCursor().position()
            for word in self.tempWords:
                if position in range(*word.position):
                    self.selectedWord = word
                    self.changeTag()
                    break

    def textIsChanged(self):
        if self.firstTextChanged:
            self.setWindowTitle('Tibetan Editor')
            self.firstTextChanged = False
        else:
            self.setWindowTitle('Tibetan Editor*')

        self.textChanged = True

        self.editor.textChanged.disconnect()

        if self.spacesModeOn or self.tagsModeOn:
            cursor = self.editor.textCursor()
            position = cursor.position()

            self.scan(tempWords=True)
            self.highlighter.highlight(
                self.tempWords, self.spacesModeOn, self.tagsModeOn, check=True)
            self.refresh()

            cursor.setPosition(position)
            self.editor.setTextCursor(cursor)

        self.editor.textChanged.connect(self.textIsChanged)

        self.checkIcon()


    def checkIcon(self):
        if self.words:
            self.spacesOpenAction.setEnabled(True)
            self.tagsOpenAction.setEnabled(True)

        if self.spacesModeOn or self.tagsModeOn:
            self.segmentAction.setEnabled(False)

        if not self.spacesModeOn and not self.tagsModeOn:
            self.segmentAction.setEnabled(True)

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
        self.toolbar.addAction(self.refreshAction)

        self.toolbar.addSeparator()
        self.toolbar.addAction(self.spacesOpenAction)
        self.toolbar.addAction(self.tagsOpenAction)

        self.toolbar.addSeparator()
        self.toolbar.addAction(self.changeTagAction)
        

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
        self.viewMenu.addAction(
            "&Spellchecker", QApplication.instance().aboutQt)
        self.viewMenu.addAction("&Highlighter", self.about)

        # Settings
        settingsMenu = self.menu.addMenu("&Help")
        settingsMenu.addAction("&Highlighter", self.about)

        self.menuBarRight = QMenuBar(self.menu)
        self.menu.setCornerWidget(self.menuBarRight, Qt.TopRightCorner)

    # Actions
    
    def about(self):
        QMessageBox.about(self, "About PyTib Editor",
                          "rules using regular expressions.</p>")

    def newFile(self):
        self.editor.clear()

    def openFile(self, path=None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(
                self, "Open File", '', "UTF-8 files (*.txt)")

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
        if not self.filename:
            self.filename, _ = QFileDialog.getSaveFileName(
                self, "Choose a file name", '.', "UTF-8 (*.txt)")

        if not self.filename:
            QMessageBox.question(self, 'Cancel', 'Illegal File Name',
                                 QMessageBox.Yes)
            return

        self.statusBar().showMessage("Saved '%s'" % self.filename, 2000)

        writer = QTextDocumentWriter(self.filename)
        success = writer.write(self.editor.document())

        self.scan()
        self.setTextByDisplayMode()
        self.textChanged = False
        self.setWindowTitle('Tibetan Editor')

        if not success:
            QMessageBox.question(self, 'Cancel', 'Saving Failed',
                                 QMessageBox.Yes)
            return

    def undo(self):
        self.editor.document().undo()

    def redo(self):
        self.editor.document().redo()

    def createActions(self):
        self.newFileAction = QAction(
            QIcon('files/filenew.png'), "&New...", self,
            shortcut=QKeySequence.New,
            statusTip="Create a new file",
            triggered=self.newFile)

        self.openFileAction = QAction(
            QIcon('files/fileopen.png'), "&Open...", self,
            shortcut=QKeySequence.Open,
            statusTip="Open a text file",
            triggered=self.openFile)

        self.saveFileAction = QAction(
            QIcon('files/filesave.png'), "&Save...", self,
            shortcut=QKeySequence.Save,
            statusTip="Save the current document",
            triggered=self.saveFile)

        self.undoAction = QAction(
            QIcon('files/editundo.png'), "&Undo", self,
                shortcut=QKeySequence.Undo,
                statusTip="Undo the last editing action",
                triggered=self.undo)

        self.redoAction = QAction(
            QIcon('files/editredo.png'), "&Redo", self,
                shortcut=QKeySequence.Redo,
                statusTip="Redo the last editing action",
                triggered=self.redo)

        self.actionQuit = QAction(
            "&Quit", self,
            shortcut="Ctrl+Q",
            triggered=self.close)

        # functions

        self.segmentAction = QAction(
            QIcon('files/segment.png'), "&Segment", self,
            triggered=self.segment)

        self.changeTagAction = QAction(
            QIcon('files/changeTag.png'), "&Change Tag", self,
            triggered=self.changeTag)

        self.spacesOpenAction = QAction(
            QIcon('files/space.png'), "&Open Spaces Mode", self,
            checkable=True, enabled=False,
            triggered=lambda: self.switchDisplayMode('Spaces'))

        self.tagsOpenAction = QAction(
            QIcon('files/tag.png'), "&Open Tags Mode", self,
            checkable=True, enabled=False,
            triggered=lambda: self.switchDisplayMode('Tags'))
        
        self.refreshAction = QAction(
            QIcon('files/refresh.png'), "&Refresh", self,
            triggered=self.refresh)

    # segment
    def segment(self):
        if self.spacesModeOn or self.tagsModeOn:
            raise Exception('Segmentation Error')

        text = self.editor.toPlainText()
        self.words = self.wordManager.segment(text)
        self.wordManager.tag(self.words)
        self.highlighter.highlight(self.words, check=True)
        # it is weird after editor.setPlainText called, the
        # highlighter.highlightBlock will be called twice but only the second
        # one works. It is because every time the highlightBlock called, the
        # format effect disappeared.
        # After profiling, we found the setFormat consumed 22% of time while
        # pasting huge block of text (about several tens of thousands words),
        # it will be slow. But we can't solve this problem at this time.
        self.updateWordsCount()
        self.setTextByDisplayMode()
        self.setWindowTitle('Tibetan Editor')

    # tag
    def changeTag(self):
        # if cursor.selectedText() not in self.partOfSpeeches:
        #     QMessageBox.question(
        #         self, 'Error', 'Please choose a part of speech.',
        #         QMessageBox.Yes)
        #     return

        self.box = QComboBox(self)
        self.box.addItems(self.partOfSpeeches)

        pos = QCursor().pos()
        self.box.setGeometry(pos.x(), pos.y(), 100, 200)
        self.box.showPopup()

        self.box.currentIndexChanged.connect(self.changing)

    def changing(self):
        tagName = self.box.currentText()

        self.editor.cursorPositionChanged.disconnect()

        cursor = self.editor.textCursor()
        cursor.setPosition(self.selectedWord.position[0])
        cursor.setPosition(self.selectedWord.position[1],
                           QTextCursor.KeepAnchor)

        cursor.insertText(tagName)
        self.editor.setTextCursor(cursor)

        self.editor.cursorPositionChanged.connect(self.cursorIsChanged)

    # display mode
    def setTextByDisplayMode(self, tempWords=False):
        if tempWords:
            words = self.tempWords
        else:
            words = self.words

        if self.spacesModeOn:
            if self.tagsModeOn:
                self.editor.setPlainText(' '.join(
                    ['{}/{}'.format(w.content, w.partOfSpeech)
                     for w in words]
                ))
            else:
                self.editor.setPlainText(' '.join(
                    [w.content for w in words]
                ))
        else:
            if self.tagsModeOn:
                self.editor.setPlainText(''.join(
                    ['{}/{}'.format(w.content, w.partOfSpeech)
                     for w in words]
                ))
            else:
                self.editor.setPlainText(''.join(
                    [w.content for w in words]
                ))

    def switchDisplayMode(self, mode):

        if self.textChanged:
            if self.firstSegment:
                self.firstSegment = False
            else:
                self.checkSaving()

        if mode == 'Spaces':
            self.spacesModeOn = not self.spacesModeOn
        elif mode == 'Tags':
            self.tagsModeOn = not self.tagsModeOn

        if not self.words[0].partOfSpeech:
            self.wordManager.tag(self.words)

        self.highlighter.highlight(
            self.words, self.spacesModeOn, self.tagsModeOn, check=True)
        self.setTextByDisplayMode()
        self.textChanged = False
        self.updateWordsCount()
        self.setWindowTitle('Tibetan Editor')

    def scan(self, tempWords=False):
        text = self.editor.toPlainText()
        words = []
        if self.spacesModeOn:
            wordStrings = text.split()
            if self.tagsModeOn:
                for wordString in wordStrings:
                    try:
                        wordStringParts = wordString.split('/')
                        word = Word(wordStringParts[0])
                        word.partOfSpeech = wordStringParts[1]
                        words.append(word)
                    except IndexError:
                        QMessageBox.question(
                            self, 'Error',
                            "Please don't edit words when tags are on.",
                            QMessageBox.Yes)
                        self.highlighter.highlight(
                            self.words, self.spacesModeOn, self.tagsModeOn)
                        self.setTextByDisplayMode()

            else:
                for wordString in wordStrings:
                    word = Word(wordString)
                    words.append(word)
        else:
            if self.tagsModeOn:
                start, end = 0, 0
                while True:
                    if any(p in text[start: end] for p in self.partOfSpeeches):
                        wordString = text[start: end]
                        wordStringParts = wordString.split('/')
                        word = Word(wordStringParts[0])
                        word.partOfSpeech = wordStringParts[1]
                        words.append(word)
                        start = end
                    else:
                        end += 1
                    if end - start >= 50:
                        break
            else:
                text = self.editor.toPlainText()
                words = self.wordManager.segment(text)

        if tempWords:
            self.tempWords = words
        else:
            self.words = words


    # Right bar and status

    def setupRightBar(self):

        # Words counting

        font = QFont()
        font.setFamily('consolas')
        font.setPointSize(16)

        wordCountWidget = QWidget()
        wordCountWidget.setObjectName('wordCountWidget')
        wordCountWidget.setStyleSheet(
            '#wordCountWidget {background-color: rgba(0, 0, 0, 0.05);}')

        fbox = QFormLayout()
        labelTitle = QLabel('Words Status:')
        labelTitle.setStyleSheet('font-weight: bold;')
        label1 = QLabel('Level 1: ')
        label2 = QLabel('Level 2: ')
        label3 = QLabel('Level 3: ')
        label4 = QLabel('Not recognized: ')

        self.level1Num = QLabel('0')
        self.level2Num = QLabel('0')
        self.level3Num = QLabel('0')
        self.levelNotFoundNum = QLabel('0')

        for label in (label1, label2, label3, label4, labelTitle,
                      self.level1Num, self.level2Num, self.level3Num, self.levelNotFoundNum):
            label.setFont(font)

        self.level1Num.setStyleSheet(
            'font-size: 200%; color: ' + self.getColorRgbaCss('level1'))
        self.level2Num.setStyleSheet(
            'font-size: 200%; color: ' + self.getColorRgbaCss('level2'))
        self.level3Num.setStyleSheet(
            'font-size: 200%; color: ' + self.getColorRgbaCss('level3'))
        self.levelNotFoundNum.setStyleSheet(
            'font-size: 200%;')

        fbox.addRow(labelTitle)
        fbox.addRow(QLabel())
        fbox.addRow(label1, self.level1Num)
        fbox.addRow(QLabel())
        fbox.addRow(label2, self.level2Num)
        fbox.addRow(QLabel())
        fbox.addRow(label3, self.level3Num)
        fbox.addRow(QLabel())
        fbox.addRow(label4, self.levelNotFoundNum)

        wordCountWidget.setLayout(fbox)

        self.wordCountWidget = wordCountWidget

    def getColorRgbaCss(self, formatName):
        return 'rgba({}, {}, {}, {})'.format(
            *(self.highlighter.getFormatColor(formatName).color().getRgb()))

    def setupColorChangeWidget(self):
        font = QFont()
        font.setFamily('consolas')
        font.setPointSize(16)

        self.colorPickerBtn1 = QPushButton()
        self.colorPickerBtn1.setText('Edit')
        self.colorPickerBtn1.setStyleSheet('background-color: ' + self.getColorRgbaCss('level1'))
        self.colorPickerBtn1.clicked.connect(
            lambda: self.changeFormatColor('level1'))

        self.colorPickerBtn2 = QPushButton()
        self.colorPickerBtn2.setText('Edit')
        self.colorPickerBtn2.setStyleSheet('background-color: ' + self.getColorRgbaCss('level2'))
        self.colorPickerBtn2.clicked.connect(
            lambda: self.changeFormatColor('level2'))

        self.colorPickerBtn3 = QPushButton()
        self.colorPickerBtn3.setText('Edit')
        self.colorPickerBtn3.setStyleSheet('background-color: ' + self.getColorRgbaCss('level3'))
        self.colorPickerBtn3.clicked.connect(
            lambda: self.changeFormatColor('level3'))

        colorChangeWidget = QWidget()
        colorChangeWidget.setObjectName('changeColorWidget')
        colorChangeWidget.setStyleSheet(
            '#changeColorWidget {background-color: rgba(0, 0, 0, 0.05);}')

        fbox = QFormLayout()
        labelTitle = QLabel('Highlight Color')
        labelTitle.setStyleSheet('font-weight: bold;')
        label1 = QLabel('Level 1 color: ')
        label2 = QLabel('Level 2 color: ')
        label3 = QLabel('Level 3 color: ')
        for label in (label1, label2, label3, labelTitle):
            label.setFont(font)

        fbox.addRow(labelTitle)
        fbox.addRow(QLabel())
        fbox.addRow(label1, self.colorPickerBtn1)
        fbox.addRow(QLabel())
        fbox.addRow(label2, self.colorPickerBtn2)
        fbox.addRow(QLabel())
        fbox.addRow(label3, self.colorPickerBtn3)

        colorChangeWidget.setLayout(fbox)

        self.changeColorWidget = colorChangeWidget

    def changeFormatColor(self, formatName):
        color = QColorDialog.getColor()
        self.highlighter.setFormatColor(formatName, color)

        formatToButtonDict = {
            'level1': self.colorPickerBtn1,
            'level2': self.colorPickerBtn2,
            'level3': self.colorPickerBtn3,
        }
        formatToLevelNumberDict = {
            'level1': self.level1Num,
            'level2': self.level2Num,
            'level3': self.level3Num,
        }
        # update button color and text color
        formatToButtonDict[formatName].setStyleSheet(
            'background-color: ' + self.getColorRgbaCss(formatName))

        formatToLevelNumberDict[formatName].setStyleSheet(
            'color: ' + self.getColorRgbaCss(formatName))

        self.setTextByDisplayMode()

    def cursorPosition(self):
        cursor = self.editor.textCursor()
        # Mortals like 1-indexed things
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber()
        self.statusBar().showMessage("Line: {} | Column: {}".format(line, col))

    # status

    def updateWordsCount(self):
        count = [0, 0, 0, 0]
        for word in self.words:
            if not word.level:
                count[0] += 1
            else:
                count[word.level] += 1

        self.level1Num.setText(str(count[1]))
        self.level2Num.setText(str(count[2]))
        self.level3Num.setText(str(count[3]))
        self.levelNotFoundNum.setText(str(count[0]))

    def checkSaving(self, yes=False):
        if yes:
            self.saveFile()
            return True
        
        choice = QMessageBox.question(
            self, 'Saving?',
            'If you want to keep the modification,\n'
            'please save the document before doing other actions,\n'
            'or the modification will be lost.',
            QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.saveFile()
            return True
        else:
            return False
    
    def refresh(self):
        self.editor.setPlainText(self.editor.toPlainText())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    window = MainWindow()
    window.show()

    exceptionHandler.errorSignal.connect(handleException)

    try:
        sys.exit(app.exec_())
    except:
        print("exiting")
        sys.exit(1)
