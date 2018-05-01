from functools import partial

from PyQt5.QtCore import Qt, QStringListModel, QSize
from PyQt5.QtGui import QTextCursor, QPalette, QIcon
from PyQt5.QtWidgets import (
    QWidget, QTextEdit, QCompleter, QComboBox, QPushButton,
    QLabel, QLineEdit, QFormLayout, QHBoxLayout, QVBoxLayout
)

class TokenWidget(QWidget):
    ATTR_CHOICES = ['Lemma', 'POS', 'Content']

    def __init__(self, parent=None):
        super().__init__(parent)
        self.attrs = []
        self.initUI()

    def initUI(self):
         # Color
        pal = QPalette()
        pal.setColor(QPalette.Background, Qt.white)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        # Buttons
        self.addAttrButton = QPushButton('add attribute')

        self.removeTokenButton = QPushButton()
        self.removeTokenButton.setFlat(True)
        self.removeTokenButton.setIconSize(QSize(25, 25))
        self.removeTokenButton.setIcon(QIcon('files\\delete.png'))
        self.removeTokenButton.clicked.connect(partial(self.removeToken, self))

        self.addAttrButton.clicked.connect(self.addAttr)

        self.fbox = QFormLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.addAttrButton, 3)
        hbox.addWidget(self.removeTokenButton, 1)
        self.fbox.addRow(hbox)

        self.addAttr()
        self.setLayout(self.fbox)

    def removeToken(self, token):
        self.addAttrButton.setParent(None)
        self.removeTokenButton.setParent(None)

        for attr in self.attrs:
            attr.itemAt(2).widget().setParent(None)
            attr.itemAt(1).widget().setParent(None)
            attr.itemAt(0).widget().setParent(None)

        self.setParent(None)

    def removeAttr(self, attr):
        attr.itemAt(2).widget().setParent(None)
        attr.itemAt(1).widget().setParent(None)
        attr.itemAt(0).widget().setParent(None)
        attr.setParent(None)
        self.attrs.remove(attr)

    def addAttr(self):
        hbox = QHBoxLayout()

        comboBox = QComboBox()
        comboBox.addItems(TokenWidget.ATTR_CHOICES)
        
        removeTokenButton = QPushButton()
        removeTokenButton.setFlat(True)
        removeTokenButton.setIconSize(QSize(25, 25))
        removeTokenButton.setIcon(QIcon('files\\delete.png'))
        removeTokenButton.clicked.connect(partial(self.removeAttr, hbox))

        hbox.addWidget(comboBox)
        hbox.addWidget(QLineEdit())
        hbox.addWidget(removeTokenButton)

        self.fbox.insertRow(self.fbox.rowCount() - 1, hbox)
        self.attrs.append(hbox)


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
