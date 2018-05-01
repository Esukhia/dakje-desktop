from collections import OrderedDict

from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QTextCursor, QPalette
from PyQt5.QtWidgets import (
    QWidget, QTextEdit, QCompleter, QComboBox, QPushButton,
    QLabel, QLineEdit, QFormLayout, QHBoxLayout, QVBoxLayout
)

class TokenWidget(QWidget):
    ATTR_CHOICES = ['Lemma', 'POS', 'Content']

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        pal = QPalette()
        pal.setColor(QPalette.Background, Qt.white)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

    def initUI(self):
        hbox = QHBoxLayout()

        comboBox = QComboBox()
        comboBox.addItems(TokenWidget.ATTR_CHOICES)
        comboBox.setStyleSheet("background-color: white;")
        hbox.addWidget(comboBox)
        hbox.addWidget(QLineEdit())

        self.addAttrButton = QPushButton('add attribute')
        self.addAttrButton.clicked.connect(self.addAttr)

        self.fbox = QFormLayout()
        self.fbox.addRow(hbox)
        self.fbox.addRow(self.addAttrButton)

        self.setLayout(self.fbox)

    def addAttr(self):
        hbox = QHBoxLayout()
        comboBox = QComboBox()
        comboBox.addItems(TokenWidget.ATTR_CHOICES)
        hbox.addWidget(comboBox)
        hbox.addWidget(QLineEdit())
        self.fbox.insertRow(self.fbox.rowCount() - 1, hbox)

class FindWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()
        self.tokens = []

    def initUI(self):
        self.fbox = QFormLayout()
        hbox = QHBoxLayout()

        self.addTokenButton = QPushButton('add token')
        self.addTokenButton.clicked.connect(self.addToken)

        self.refreshTextButton = QPushButton('refresh text')
        self.refreshTextButton.clicked.connect(self.refreshText)

        hbox.addWidget(self.addTokenButton, 1)
        hbox.addWidget(self.refreshTextButton, 1)

        self.fbox.addRow(hbox)
        self.setLayout(self.fbox)

    def addToken(self):
        token = TokenWidget()
        self.tokens.append(token)
        self.fbox.insertRow(self.fbox.rowCount() - 1, token)

    def refreshText(self):
        pass
