#!/usr/local/bin/env python3.5
# -*- coding: utf-8 -*-
import sys
import copy

from PyQt5 import QtCore
from PyQt5.QtCore import QFile, Qt, QStringListModel
from PyQt5.QtGui import QFont, QIcon, QKeySequence, QTextDocumentWriter, QCursor, QTextCursor
from PyQt5.QtWidgets import (
    QAction, QApplication, QFormLayout, QFileDialog, QGridLayout, QLabel, QListView, QCompleter,
    QColorDialog, QMainWindow, QMenuBar, QMessageBox, QPushButton, QComboBox, QMenu,
    QInputDialog, QStyleFactory, QTextEdit, QWidget, QAbstractItemView, QStyledItemDelegate)

from highlighter import Highlighter
from Word import WordManager, Word
from find import FindDialog

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

class ComboBox(QComboBox):
    def hidePopup(self):
        pass

    def hideManually(self):
        QComboBox.hidePopup(self)

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.filename = None
        self.spacesModeOn = False
        self.tagsModeOn = False

        self.textChanged = False
        self.firstSegment = True

        self.currentPosition = 0
        self.previousPosition = 0

        self.currentSelection = {
            'selected': False,
            'start': None,
            'end': None}
        self.previousSelection = {
            'selected': False,
            'start': None,
            'end': None}

        self.words = []
        self.wordManager = WordManager()
        self.partOfSpeeches = self.wordManager.getPartOfSpeeches()

        self.initUI()

        self.setWindowTitle("Tibetan Editor")
        self.setWindowIcon(QIcon("tab1.png"))
        self.setWindowState(Qt.WindowMaximized)
        self.resize(1200, 480)


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

    ###

    def setupEditor(self):
        font = QFont()
        # font.setFamily('Noto Sans Tibetan')
        font.setFixedPitch(True)
        font.setPointSize(15)

        self.editor = QTextEdit()
        self.editor.setFont(font)
        self.editor.cursorPositionChanged.connect(self.cursorIsChanged)
        self.editor.textChanged.connect(self.textIsChanged)
        self.editor.mousePressEvent = self.mouseIsPressed

        self.highlighter = Highlighter(self.editor.document())

    def cursorIsChanged(self):
        cursor = self.editor.textCursor()

        self.updateStatusBar(cursor)

        self.previousPosition = self.currentPosition
        self.currentPosition = cursor.position()

        self.previousSelection = self.currentSelection

        if cursor.hasSelection():
            self.currentSelection = {
                'selected': True,
                'start': cursor.selectionStart(),
                'end': cursor.selectionEnd()
            }
        else:
            self.currentSelection = {
                'selected': False,
                'start': None,
                'end': None
            }

    def updateStatusBar(self, cursor):
        # Mortals like 1-indexed things
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber()
        self.statusBar().showMessage("Line: {} | Column: {}".format(line, col))

    def textIsChanged(self):
        if self.words:
            if not self.editor.toPlainText():
                self.words = []

            if self.previousSelection['selected']:
                shift = self.currentPosition - self.previousPosition

                deletedIndex = []

                for index, word in enumerate(self.words):
                    if self.previousSelection['start'] < word.start < self.previousSelection['end'] or \
                            self.previousSelection['end'] > word.end >= self.previousSelection['start']:
                        deletedIndex.append(index)

                    if word.start >= self.previousPosition:
                        word.start += shift

                for index in reversed(deletedIndex):
                    self.words.pop(index)

            else:
                shift = self.currentPosition - self.previousPosition
                # 推位移
                for word in self.words:
                    if word.start >= self.previousPosition:
                        word.start += shift

                # 處理那個字
                if not self.spacesModeOn:
                    removedList = []
                    for i, word in enumerate(self.words):
                        if word.start + 1 <= self.previousPosition <= word.end:
                            removedList.append(i)

                    for i in reversed(removedList):
                        self.words.pop(i)
                else:
                    newWords = []
                    newWords2 = []
                    initPos = None
                    for index, word in enumerate(self.words):
                        # split words
                        if word.start < self.currentPosition <= word.end:
                            initPos = word.start
                            text = self.editor.toPlainText()
                            sentence = text[
                                word.start: self.words[index + 1].start]
                            words = sentence.split()
                            newWords.append((index, words))
                            break


                        if word.start == self.currentPosition:
                            # concat words
                            if self.words[index - 1].end + 1 == self.currentPosition:
                                initPos = self.words[index - 1].start
                                text = self.editor.toPlainText()
                                word = text[
                                    self.words[index - 1].start:
                                    self.words[index].end + 1]
                                newWords2.append((index - 1, [word]))
                                break

                            # 在字首加字
                            else:
                                initPos = word.start - 1
                                text = self.editor.toPlainText()
                                word = text[word.start - 1:
                                            word.end]
                                newWords.append((index, [word]))
                                break

                    for index, words in reversed(newWords):
                        words = [Word(word) for word in words]
                        self.wordManager.tag(words)
                        self.wordManager.checkLevel(words)
                        self.calStart(words, initPos=initPos)
                        self.words[index: index + 1] = words

                    for index, words in reversed(newWords2):
                        words = [Word(word) for word in words]
                        self.wordManager.tag(words)
                        self.wordManager.checkLevel(words)
                        self.calStart(words, initPos=initPos)
                        self.words[index: index + 2] = words



            self.highlighter.setWords(self.words)
            self.highlight()

        self.textChanged = True
        self.updateWordsCount()
        # self.setWindowTitle('Tibetan Editor*')

    def highlight(self):
        self.highlighter.setWords(self.words)
        self.highlighter.setHighLightBlock(True)

        self.editor.textChanged.disconnect()
        self.highlighter.rehighlight()
        self.editor.textChanged.connect(self.textIsChanged)

        self.highlighter.setHighLightBlock(False)

    # segment
    def segment(self):
        if self.words:
            text = self.editor.toPlainText()
            wordIndex = 0
            charIndex = 0
            sentence = ''
            insertedWords = []
            while True:
                if wordIndex == len(self.words) - 1:
                    break

                if self.words[wordIndex].end >= charIndex >= self.words[wordIndex].start:
                    charIndex += 1

                elif charIndex >= self.words[wordIndex + 1].start:
                    if sentence:
                        words = self.wordManager.segment(sentence)
                        sentence = ''
                        insertedWords.append((wordIndex + 1, words))

                    wordIndex += 1

                else:
                    sentence += text[charIndex]
                    charIndex += 1

            shift = 0
            for words in insertedWords:
                self.wordManager.tag(words[1])
                self.wordManager.checkLevel(words[1])

                for word in words[1]:
                    self.words.insert(words[0] + shift, word)
                    shift += 1

        else:
            text = self.editor.toPlainText()
            self.words = self.wordManager.segment(text)
            self.wordManager.tag(self.words)
            self.wordManager.checkLevel(self.words)

        self.setTextByDisplayMode()
        self.highlight()

        self.tagsOpenAction.setEnabled(True)
        self.spacesOpenAction.setEnabled(True)

        self.updateWordsCount()

    ###

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

        self.toolbar.addSeparator()
        self.toolbar.addAction(self.spacesOpenAction)
        self.toolbar.addAction(self.tagsOpenAction)
        self.toolbar.addAction(self.findAction)

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

        self.spacesOpenAction = QAction(
            QIcon('files/space.png'), "&Open Spaces Mode", self,
            checkable=True, enabled=False,
            triggered=lambda: self.switchDisplayMode('Spaces'))

        self.tagsOpenAction = QAction(
            QIcon('files/tag.png'), "&Open Tags Mode", self,
            checkable=True, enabled=False,
            triggered=lambda: self.switchDisplayMode('Tags'))

        self.findAction = QAction(
            QIcon('files/searching.png'), "&Find & Replace", self,
            triggered=FindDialog(self).show)

    def setTextByDisplayMode(self):
        self.editor.textChanged.disconnect()
        self.editor.setPlainText(self.calStart(self.words))
        self.editor.textChanged.connect(self.textIsChanged)


    def calStart(self, words, initPos=0):
        text = []
        end = initPos
        for word in words:
            start = end
            end = start + len(word.content)

            text.append(word.content)
            word.start = start

            if self.tagsModeOn:
                text.append('/')
                text.append(word.partOfSpeech)
                word.tagIsOn = True
                end += word.partOfSpeechLen
            else:
                word.tagIsOn = False

            if self.spacesModeOn:
                text.append(' ')
                end += 1

        return ''.join(text)

    # tag
    def mouseIsPressed(self, event):
        QTextEdit.mousePressEvent(self.editor, event)

        if self.tagsModeOn:
            position = self.editor.textCursor().position()
            for word in self.words:
                if position in range(
                        word.partOfSpeechStart, word.partOfSpeechEnd + 1):
                    self.selectedWord = word
                    self.changeTag(event.pos())
                    break

    def changeTag(self, pos):
        self.editor.box = ComboBox(self.editor)
        self.editor.box.setStyleSheet('font-size: 16px;')
        self.editor.box.addItems(self.partOfSpeeches)
        self.editor.box.setGeometry(pos.x(), pos.y() + 16, 50, 80)
        self.editor.box.activated.connect(self.changing)
        self.editor.box.showPopup()

    def changing(self):
        tagName = self.editor.box.currentText()
        self.editor.box.hideManually()

        self.editor.cursorPositionChanged.disconnect()

        self.selectedWord.partOfSpeech = tagName
        self.setTextByDisplayMode()
        self.highlight()

        self.editor.cursorPositionChanged.connect(self.cursorIsChanged)

    def switchDisplayMode(self, mode):
        if mode == 'Spaces':
            self.spacesModeOn = not self.spacesModeOn
        elif mode == 'Tags':
            self.tagsModeOn = not self.tagsModeOn

        if self.words:
            if not self.words[0].partOfSpeech:
                self.wordManager.tag(self.words)

        self.setTextByDisplayMode()
        self.highlight()
        self.textChanged = False
        self.setWindowTitle('Tibetan Editor')

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
        current_color = self.highlighter.getFormatColor(formatName).color()
        color = QColorDialog.getColor(initial=current_color)
        if color.isValid():
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
