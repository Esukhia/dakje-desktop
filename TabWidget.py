#!/usr/local/bin/env python3.5
# -*- coding: utf-8 -*-

import textwrap

from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QWidget, QTabWidget, QFormLayout, QHBoxLayout, QVBoxLayout,
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
        button.setIcon(QIcon('files/add.png'))
        button.clicked.connect(partial(self.addNewFormat, 'level'))

        # Name and button
        hbox2 = QHBoxLayout()
        hbox2.addWidget(QLabel('Name'))
        hbox2.addWidget(button)

        # Titles
        hbox = QHBoxLayout()
        hbox.addLayout(hbox2)
        hbox.addWidget(QLabel('Color'))
        hbox.addWidget(QLabel('List'))
        hbox.addWidget(QLabel('Rule'))
        hbox.addWidget(QLabel('Delete'))

        self.levelFormLayout = QFormLayout()
        self.levelFormLayout.addRow(hbox)
        self.levelTab.setLayout(self.levelFormLayout)

    def initPosTab(self):
        # Adding button
        button = QPushButton()
        button.setIcon(QIcon('files/add.png'))
        button.clicked.connect(partial(self.addNewFormat, 'pos'))

        # Name and button
        hbox2 = QHBoxLayout()
        hbox2.addWidget(QLabel('Name'))
        hbox2.addWidget(button)

        # Titles
        hbox = QHBoxLayout()
        hbox.addLayout(hbox2)
        hbox.addWidget(QLabel('Color'))
        hbox.addWidget(QLabel('Rule'))
        hbox.addWidget(QLabel('Delete'))

        self.posFormLayout = QFormLayout()
        self.posFormLayout.addRow(hbox)
        self.posTab.setLayout(self.posFormLayout)

    def addTextFormat(self, textFormat):
        hbox = QHBoxLayout()

        # Name
        self.buttons.append(QPushButton())
        textFormat.editButton = self.buttons[-1]
        textFormat.editButton.setText('Edit')
        textFormat.editButton.clicked.connect(
            partial(self.changeName, textFormat))

        textFormat.nameLabel = QLabel(textFormat.name)
        vbox = QVBoxLayout()
        vbox.addWidget(textFormat.nameLabel)
        vbox.addWidget(textFormat.editButton)
        hbox.addLayout(vbox)

        # ColorButton
        self.buttons.append(QPushButton())
        textFormat.colorButton = self.buttons[-1]
        textFormat.colorButton.setText('Edit')
        textFormat.colorButton.setStyleSheet(
            'background-color: ' + textFormat.getColorRgbaCss())
        textFormat.colorButton.clicked.connect(
            partial(self.changeColor, textFormat))
        hbox.addWidget(textFormat.colorButton)

        # ListButton
        if textFormat.type == 'level':
            self.buttons.append(QPushButton())
            textFormat.listButton = self.buttons[-1]
            textFormat.listButton.clicked.connect(
                partial(self.openFile, textFormat, type='list'))
            hbox.addWidget(textFormat.listButton)

        # RuleButton
        self.buttons.append(QPushButton())
        textFormat.ruleButton = self.buttons[-1]
        textFormat.ruleButton.clicked.connect(
            partial(self.openFile, textFormat, type='rule'))
        hbox.addWidget(textFormat.ruleButton)

        # DeleteButton
        self.buttons.append(QPushButton())
        textFormat.removeButton = self.buttons[-1]
        textFormat.removeButton.clicked.connect(
            partial(self.parent.textFormatManager.remove, textFormat))
        textFormat.removeButton.setIcon(QIcon('files/delete.png'))
        hbox.addWidget(textFormat.removeButton)

        textFormat.tabHBox = hbox
        if textFormat.type == 'level':
            self.levelFormLayout.addRow(hbox)
        else:
            self.posFormLayout.addRow(hbox)

    def addNewFormat(self, type):
        textFormat = TextFormat('(New Format)', type)
        self.parent.textFormatManager.insert(textFormat)

    def removeTextFormat(self, textFormat):
        for i in reversed(range(textFormat.tabHBox.count())):
            if i == 0:
                vbox = textFormat.tabHBox.itemAt(i)
                for j in reversed(range(vbox.count())):
                    vbox.itemAt(j).widget().setParent(None)
            else:
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
        text, _ = QInputDialog.getText(self.parent, 'Name', 'Please enter a name:')
        textFormat.name = text
        textFormat.nameLabel.setText(textFormat.name)
        textFormat.counterNameLabel.setText(textFormat.name)
        self.parent.highlightViewpoint()

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
