#!/usr/local/bin/env python3.5
# -*- coding: utf-8 -*-

import textwrap

from functools import partial

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QWidget, QTabWidget, QFormLayout, QHBoxLayout, QVBoxLayout, QLineEdit,
    QColorDialog, QFileDialog, QInputDialog, QLabel, QPushButton
)

from TextFormat import TextFormat

# deal with buttons: https://stackoverflow.com/questions/17425367/pyqt4-create-many-buttons-from-dict-dynamically

class TabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.buttons = []

        self.levelTab = QWidget()
        self.posTab = QWidget()
        self.initLevelTab()
        self.initPosTab()
        self.addTab(self.levelTab, "LEVEL")
        self.addTab(self.posTab, "POS")

    def initLevelTab(self):
        # Adding button
        button = QPushButton()
        button.setFlat(True)
        button.setIconSize(QSize(30, 30))
        button.setIcon(QIcon('files/add.png'))
        button.clicked.connect(partial(self.addNewFormat, 'level'))

        # Titles
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Name'), 3)
        hbox.addWidget(QLabel('Color'), 3)
        hbox.addWidget(QLabel('List'), 3)
        hbox.addWidget(QLabel('Rule'), 3)
        hbox.addWidget(QLabel(), 1)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(button, alignment=Qt.AlignCenter)
        hbox2.addStretch()

        self.levelFormLayout = QFormLayout()
        self.levelFormLayout.addRow(hbox)
        self.levelFormLayout.addRow(hbox2)
        self.levelTab.setLayout(self.levelFormLayout)

    def initPosTab(self):
        # Adding button
        button = QPushButton()
        button.setFlat(True)
        button.setIconSize(QSize(30, 30))
        button.setIcon(QIcon('files/add.png'))
        button.clicked.connect(partial(self.addNewFormat, 'pos'))

        # Titles
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Name'), 3)
        hbox.addWidget(QLabel('Color'), 3)
        hbox.addWidget(QLabel('Rule'), 3)
        hbox.addWidget(QLabel(), 1)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(button)
        hbox2.addStretch()

        self.posFormLayout = QFormLayout()
        self.posFormLayout.addRow(hbox)
        self.posFormLayout.addRow(hbox2)
        self.posTab.setLayout(self.posFormLayout)

    def addTextFormat(self, textFormat):
        hbox = QHBoxLayout()

        # Name
        self.buttons.append(QPushButton())
        textFormat.editButton = self.buttons[-1]
        textFormat.editButton.setText(textFormat.name)
        textFormat.editButton.setFlat(True)
        textFormat.editButton.clicked.connect(
            partial(self.changeName, textFormat))
        hbox.addWidget(textFormat.editButton, 3)

        # ColorButton
        self.buttons.append(QPushButton())
        textFormat.colorButton = self.buttons[-1]
        textFormat.colorButton.setText('Edit')
        textFormat.colorButton.setStyleSheet(
            'background-color: ' + textFormat.getColorRgbaCss())
        textFormat.colorButton.clicked.connect(
            partial(self.changeColor, textFormat))
        hbox.addWidget(textFormat.colorButton, 3)

        # ListButton
        if textFormat.type == 'level':
            self.buttons.append(QPushButton())
            textFormat.listButton = self.buttons[-1]
            textFormat.listButton.clicked.connect(
                partial(self.openFile, textFormat, type='list'))
            hbox.addWidget(textFormat.listButton, 3)

        # RuleButton
        self.buttons.append(QPushButton())
        textFormat.ruleButton = self.buttons[-1]
        textFormat.ruleButton.clicked.connect(
            partial(self.openFile, textFormat, type='rule'))
        hbox.addWidget(textFormat.ruleButton, 3)

        # DeleteButton
        self.buttons.append(QPushButton())
        textFormat.removeButton = self.buttons[-1]
        textFormat.removeButton.setFlat(True)
        textFormat.removeButton.setIconSize(QSize(25, 25))
        textFormat.removeButton.clicked.connect(
            partial(self.parent.textFormatManager.remove, textFormat))
        textFormat.removeButton.setIcon(QIcon('files/delete.png'))
        hbox.addWidget(textFormat.removeButton, 1)

        textFormat.tabHBox = hbox
        if textFormat.type == 'level':
            row = self.levelFormLayout.rowCount() - 1
            self.levelFormLayout.insertRow(row, hbox)
        else:
            row = self.posFormLayout.rowCount() - 1
            self.posFormLayout.insertRow(row, hbox)

    def addNewFormat(self, type):

        def getLatestNumber(formats, matchString):
            i = 1
            while True:
                if '{}{}'.format(matchString, i) in [
                        f.name for f in formats]:
                    i += 1
                else:
                    break
            return i

        if type == 'level':
            textFormat = TextFormat('Level' + str(getLatestNumber(
                self.parent.textFormatManager.getFormats(type='level'), 'Level')
            ), type)
        else:
            textFormat = TextFormat('POS' + str(getLatestNumber(
                self.parent.textFormatManager.getFormats(type='pos'), 'POS')
            ), type)
        self.parent.textFormatManager.insert(textFormat)

    def removeTextFormat(self, textFormat):
        for i in reversed(range(textFormat.tabHBox.count())):
            textFormat.tabHBox.itemAt(i).widget().setParent(None)

        if textFormat.type == 'level':
            self.levelFormLayout.removeItem(textFormat.tabHBox)
        else:
            self.posFormLayout.removeItem(textFormat.tabHBox)

    def changeColor(self, textFormat):
        color = QColorDialog.getColor(initial=textFormat.getColor())
        if color.isValid():
            textFormat.setColor(color)
            textFormat.colorButton.setStyleSheet(
                'background-color: ' + textFormat.getColorRgbaCss())

            self.parent.highlightViewpoint()

    def changeName(self, textFormat):
        textFormat.editButton.setParent(None)
        self.nameLineEdit = QLineEdit()
        textFormat.tabHBox.insertWidget(0, self.nameLineEdit, stretch=3)
        self.nameLineEdit.setFocus()
        self.nameLineEdit.returnPressed.connect(self.getChangedName)
        self.nameLineEdit.focusOutEvent = self.nameLineEditFocusOut
        self.textFormat = textFormat

    def nameLineEditFocusOut(self, event):
        QLineEdit.focusOutEvent(self.nameLineEdit, event)
        self.getChangedName()

    def getChangedName(self):
        name = self.nameLineEdit.text()
        if name:
            self.textFormat.editButton.setText(name)
            self.textFormat.counterNameLabel.setText(name)
        self.nameLineEdit.setParent(None)
        self.textFormat.tabHBox.insertWidget(0, self.textFormat.editButton, stretch=3)

    def openFile(self, textFormat, type):
        filePath, _ = QFileDialog.getOpenFileName(self)
        if filePath:
            if type == 'list':
                textFormat.setupWordList(filePath)
                listName = filePath.split('/')[-1]
                textFormat.listButton.setText(
                    listName[:10] + '..' if len(listName) > 10 else listName)

            elif type == 'rule':
                ok = textFormat.setupRegexList(filePath)
                if ok:
                    ruleName = filePath.split('/')[-1]
                    textFormat.ruleButton.setText(
                        ruleName[:10] + '..' if len(ruleName) > 10 else ruleName)
                else:
                    textFormat.ruleButton.setText('')

            self.parent.highlightViewpoint()
            self.parent.counterWidget.refresh()
