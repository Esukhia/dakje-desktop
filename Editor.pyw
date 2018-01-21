#!/usr/local/bin/env python3.5
# -*- coding: utf-8 -*-
import os
import sys
import logging
import datetime

import textwrap

from PyQt5 import QtCore
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QIcon,  QTextCursor
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
from TabWidget import TabWidget
from CounterWidget import CounterWidget

from BasicEditor import BasicEditor


class ExceptionHandler(QtCore.QObject):
    errorSignal = QtCore.pyqtSignal()

    def __init__(self):
        super(ExceptionHandler, self).__init__()

    def handler(self, exctype, value, traceback):
        logging.basicConfig(filename='Error.log', level=logging.DEBUG)
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

class TibetanEditor(BasicEditor):

    def __init__(self, parent=None):
        self.modeManager = ModeManager(self)
        self.wordManager = WordManager(self)
        self.textFormatManager = TextFormatManager(self)
        self.profileManager = ProfileManager(self)
        self.eventHandler = EventHandler(self)

        self.forceClose = False

        super().__init__(parent)

        self.setWindowTitle("Untitled (default.profile) - TibetanEditor")

        if not os.path.exists('default.profile'):
            self.profileManager.saveProfile(filePath='default.profile')
        self.profileManager.openProfile(filePath='default.profile')

    def closeEvent(self, *args, **kwargs):
        if not self.forceClose:
            self.eventHandler.checkSaving()
            self.profileManager.saveProfile(filePath='default.profile')
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
        self.tabWidget = TabWidget(self)
        self.counterWidget = CounterWidget(self)
        widget = QWidget()

        vbox = QVBoxLayout()
        vbox.addWidget(self.tabWidget, 1)
        vbox.addWidget(self.counterWidget, 1)

        hbox = QHBoxLayout()
        hbox.addWidget(self.textEdit, 3)
        hbox.addLayout(vbox, 1)

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

    def createActions(self):
        super().createActions()
        self.segmentAction = QAction(
            QIcon('files/segment.png'), "&Segment", self,
            triggered=self.segment)

        self.spacesOpenAction = QAction(
            QIcon('files/space.png'), "&Open Spaces Mode", self,
            checkable=True, enabled=False,
            triggered=lambda: self.modeManager.switchDisplayMode('Spaces'))

        self.tagsOpenAction = QAction(
            QIcon('files/tag.png'), "&Open Tags Mode", self,
            checkable=True, enabled=False,
            triggered=lambda: self.modeManager.switchDisplayMode('Tags'))

        self.findAction = QAction(
            QIcon('files/searching.png'), "&Find & Replace", self,
            triggered=FindDialog(self).show)

        self.saveProfileAction = QAction(
            QIcon('files/export.png'), "&Export profile", self,
            triggered=self.profileManager.saveProfile)

        self.openProfileAction = QAction(
            QIcon('files/import.png'), "&Import profile", self,
            triggered=self.profileManager.openProfile)

    # segment
    def segment(self):
        text = self.textEdit.toPlainText()

        for start, end, index in reversed(
                self.wordManager.getNoSegBlocks(textLen=len(text))):

            print(start, end, index)

            newWords = self.wordManager.segment(text[start:end])
            self.wordManager.tag(newWords)
            self.wordManager.insertWordsByIndex([(newWords, index)])

        self.modeManager.setText()
        self.highlightViewpoint(
            currentBlock=self.textEdit.document().firstBlock())

        self.spacesOpenAction.setEnabled(True)
        self.tagsOpenAction.setEnabled(True)

        # tag
    def changeTag(self, point):
        self.box = QComboBox()
        self.box.addItems(self.wordManager.getPartOfSpeeches())
        self.box.setGeometry(point.x(), point.y() + 100, 100, 200)
        self.box.activated.connect(self.changing)
        self.box.showPopup()

    def changing(self):
        tagName = self.box.currentText()
        self.selectedWord.partOfSpeech = tagName
        self.modeManager.setText()
        self.highlightViewpoint()

    # highlight
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


if __name__ == '__main__':
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
