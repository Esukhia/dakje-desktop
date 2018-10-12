#!/usr/local/bin/env python3.5
# -*- coding: utf-8 -*-
import os
import sys
import logging
import datetime

import textwrap

from appdirs import user_data_dir

from PyQt5 import QtCore
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QIcon, QTextCursor, QFont
from PyQt5.QtWidgets import (QAction, QApplication, QComboBox,
                             QStyleFactory, QWidget, QMessageBox,
                             QHBoxLayout, QVBoxLayout)

from highlighter import Highlighter

from TextFormat import TextFormat, TextFormatManager
from Profile import ProfileManager
from Mode import ModeManager
from Word import Word, WordManager
from EventHandler import EventHandler

from find import FindDialog
from widgets import ProfileWidget, CounterWidget, FindWidget, \
    DictionaryEditorWidget

from BasicEditor import BasicEditor


class ExceptionHandler(QtCore.QObject):
    errorSignal = QtCore.pyqtSignal()

    def __init__(self):
        super(ExceptionHandler, self).__init__()

    def handler(self, exctype, value, traceback):
        logging.basicConfig(level=logging.DEBUG)
        logging.info('========================================')
        logging.info('Time: ' + str(datetime.datetime.now()))
        logging.error("Uncaught exception\n",
                      exc_info=(exctype, value, traceback))
        logging.info('========================================')

        self.errorSignal.emit()
        sys._excepthook(exctype, value, traceback)


exceptionHandler = ExceptionHandler()
sys._excepthook = sys.excepthook
sys.excepthook = exceptionHandler.handler

EXECUTING_TYPE = None
NORMAL = 0
PYINSTALLER = 1
NSIS = 2

if hasattr(sys, '_MEIPASS'):
    # pyinstaller will add _MEIPASS variable to sys
    # which indicates the executing script's directory
    EXECUTING_TYPE = PYINSTALLER
else:
    EXECUTING_TYPE = NORMAL

if EXECUTING_TYPE == PYINSTALLER:
    BASE_DIRECTORY = sys._MEIPASS
else:
    directory = os.path.dirname(os.path.realpath(__file__))
    BASE_DIRECTORY = directory if os.path.basename(directory) == "tibetaneditor" \
        else os.path.dirname(directory)
os.chdir(BASE_DIRECTORY)

APP_NAME = "Tibetan Editor"
SETTINGS_DIRECTORY = user_data_dir(APP_NAME, appauthor=False)

class TibetanEditor(BasicEditor):
    APP_NAME = "Tibetan Editor"
    SETTINGS_DIRECTORY = SETTINGS_DIRECTORY

    def __init__(self, parent=None):
        os.makedirs(SETTINGS_DIRECTORY, exist_ok=True) 

        self.modeManager = ModeManager(self)
        self.wordManager = WordManager(self)
        self.textFormatManager = TextFormatManager(self)
        self.profileManager = ProfileManager(self)
        self.eventHandler = EventHandler(self)

        self.forceClose = False

        super().__init__(parent)

        self.setWindowTitle("Untitled (default.profile) - TibetanEditor")

        defaultProfilePath = os.path.join(SETTINGS_DIRECTORY, 'default.profile')
        if not os.path.exists(defaultProfilePath):
            self.profileManager.saveProfile(filePath=defaultProfilePath)
        self.profileManager.openProfile(filePath=defaultProfilePath)

    def closeEvent(self, *args, **kwargs):
        if not self.forceClose:
            self.eventHandler.checkSaving()
            self.profileManager.saveProfile(
                filePath=os.path.join(SETTINGS_DIRECTORY, 'default.profile'))
        super().closeEvent(*args, **kwargs)

    def handleException(self):
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Critical)
        self.msg.setWindowTitle('Error!!')
        self.msg.setText("An error occurred.\n"
                         "If the problem happens repeatedly,\n"
                         "please send the 'Error.log' file\n"
                         "to the developer.")
        self.msg.show()

        self.forceClose = True
        self.close()

    def newFile(self):
        if self.textEdit.toPlainText() != "":
            self.eventHandler.checkSaving()
        super().newFile()
        self.filename = "Untitled (default.profile) - TibetanEditor"
        self.eventHandler.changedWithoutSaving = False
        self.eventHandler.checkTitle()

    def saveFile(self):
        super().saveFile()
        self.eventHandler.changedWithoutSaving = False
        self.eventHandler.checkTitle()
        self.setWindowTitle(
            self.filename.split('/')[-1] + ' ' +
            ' '.join(self.windowTitle().split(' ')[1:]))

    def openFile(self):
        self.eventHandler.checkSaving()
        super().openFile()
        self.eventHandler.changedWithoutSaving = False
        self.eventHandler.checkTitle()

        self.setWindowTitle(
            self.filename.split('/')[-1] + ' ' +
            ' '.join(self.windowTitle().split(' ')[1:]))

    def setupLayout(self):
        self.profileWidget = ProfileWidget(self)
        self.counterWidget = CounterWidget(self)
        self.findWidget = FindWidget(self)

        widget = QWidget()

        rightVBox = QVBoxLayout()
        rightVBox.addWidget(self.profileWidget, 1)
        rightVBox.addWidget(self.counterWidget, 1)

        leftVBox = QVBoxLayout()
        leftVBox.addWidget(self.findWidget, 1)

        hbox = QHBoxLayout()
        hbox.addLayout(leftVBox, 1)
        hbox.addWidget(self.textEdit, 3)
        hbox.addLayout(rightVBox, 1)

        widget.setLayout(hbox)
        self.setCentralWidget(widget)

    def setupTextEdit(self):
        super().setupTextEdit()
        self.highlighter = Highlighter(self.textEdit.document(),
                                       mainWindow=self)

        self.textEdit.cursorPositionChanged.connect(
            self.eventHandler.cursorPositionChanged)
        self.textEdit.textChanged.connect(
            self.eventHandler.textChanged)

        self.textEdit.mousePressEvent = self.eventHandler.mousePressEvent
        self.textEdit.wheelEvent = self.eventHandler.wheelEvent

        self.textEdit.verticalScrollBar().sliderReleased.connect(
            self.highlightViewpoint)

    def setupToolBar(self):
        super().setupToolBar()
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.segmentAction)

        self.toolbar.addSeparator()
        self.toolbar.addAction(self.spacesOpenAction)
        self.toolbar.addAction(self.tagsOpenAction)
        self.toolbar.addAction(self.findAction)

        self.toolbar.addSeparator()
        self.toolbar.addAction(self.openProfileAction)
        self.toolbar.addAction(self.saveProfileAction)

        # self.toolbar.addSeparator()
        # self.toolbar.addAction(self.openDictionaryEditorAction)

    def createActions(self):
        super().createActions(BASE_DIRECTORY)
        self.segmentAction = QAction(
            QIcon(os.path.join(BASE_DIRECTORY, 'files/segment.png')),
            "&Segment", self, triggered=self.segment)

        self.spacesOpenAction = QAction(
            QIcon(os.path.join(BASE_DIRECTORY, 'files/space.png')),
            "&Open Spaces Mode", self,
            checkable=True, enabled=False,
            triggered=lambda: self.modeManager.switchDisplayMode('Spaces'))

        self.tagsOpenAction = QAction(
            QIcon(os.path.join(BASE_DIRECTORY, 'files/tag.png')),
            "&Open Tags Mode", self,
            checkable=True, enabled=False,
            triggered=lambda: self.modeManager.switchDisplayMode('Tags'))

        self.findAction = QAction(
            QIcon(os.path.join(BASE_DIRECTORY, 'files/searching.png')),
            "&Find & Replace", self,
            triggered=FindDialog(self).show)

        self.saveProfileAction = QAction(
            QIcon(os.path.join(BASE_DIRECTORY, 'files/export.png')),
            "&Export profile", self,
            triggered=self.profileManager.saveProfile)

        self.openProfileAction = QAction(
            QIcon(os.path.join(BASE_DIRECTORY, 'files/import.png')),
            "&Import profile", self,
            triggered=self.profileManager.openProfile)

        self.openDictionaryEditorAction = QAction(
            QIcon(os.path.join(BASE_DIRECTORY, 'files/dictionary.png')),
            "&Open dictionary editor", self,
            triggered=lambda: DictionaryEditorWidget(self).show())

    # segment
    def segment(self, keepCursor=False):
        text = self.textEdit.toPlainText()

        for start, end, index in reversed(
                self.wordManager.getNoSegBlocks(textLen=len(text))):
            newWords = self.wordManager.segment(text[start:end])
            self.wordManager.insertWordsByIndex([(newWords, index)])

        self.modeManager.setText(keepCursor)
        self.highlightViewpoint(
            currentBlock=self.textEdit.document().firstBlock())

        self.spacesOpenAction.setEnabled(True)
        self.tagsOpenAction.setEnabled(True)

        # tag

    def changeTag(self, point):
        self.box = QComboBox(self.textEdit)
        self.box.addItems(self.wordManager.getPartOfSpeeches())

        font = QFont()
        font.setFixedPitch(True)
        font.setPointSize(12)

        self.box.setFont(font)
        self.box.setGeometry(point.x(), point.y(), 80, 100)
        self.box.activated.connect(self.changing)
        self.box.showPopup()

    def changing(self):
        tagName = self.box.currentText()
        self.selectedWord.partOfSpeech = tagName
        self.modeManager.setText()
        self.highlightViewpoint()

    def highlightViewpoint(self, currentBlock=None):
        cursor = self.textEdit.cursorForPosition(QPoint(0, 0))
        bottom_right = QPoint(self.textEdit.viewport().width() - 1,
                              self.textEdit.viewport().height() - 1)
        end_pos = self.textEdit.cursorForPosition(bottom_right).position()
        cursor.setPosition(end_pos, QTextCursor.KeepAnchor)

        self.highlighter.formatList = self.textFormatManager.getFormats()
        self.highlighter.highLightBlockOn = True
        self.textEdit.textChanged.disconnect()

        viewPointStart = cursor.selectionStart()
        viewPointEnd = cursor.selectionEnd()

        if not currentBlock:
            textCursor = self.textEdit.textCursor()
            textCursor.setPosition(viewPointStart)
            currentBlock = textCursor.block()

        while True:
            if (not currentBlock.isValid() or
                    currentBlock.position() > viewPointEnd):
                break
            self.highlighter.rehighlightBlock(currentBlock)
            currentBlock = currentBlock.next()

        self.textEdit.textChanged.connect(self.eventHandler.textChanged)
        self.highlighter.highLightBlockOn = False

    def selectWord(self, start, end):
        words = self.wordManager.getWords()
        self.setSelection(words[start].start, words[end].modeEnd)

    def setSelection(self, start, end):
        cursor = self.textEdit.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        self.textEdit.setTextCursor(cursor)


def main():
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    window = TibetanEditor()
    window.show()

    exceptionHandler.errorSignal.connect(window.handleException)

    try:
        sys.exit(app.exec_())
    except:
        print("exiting")
        sys.exit(1)


if __name__ == '__main__':
    main()
