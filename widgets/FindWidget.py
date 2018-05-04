from functools import partial

from PyQt5.QtCore import Qt, QStringListModel, QSize
from PyQt5.QtGui import QTextCursor, QPalette, QIcon
from PyQt5.QtWidgets import (
    QWidget, QTextEdit, QCompleter, QComboBox, QPushButton,
    QLabel, QLineEdit, QFormLayout, QHBoxLayout, QVBoxLayout
)

from collections import OrderedDict

from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import (
    QWidget, QTextEdit, QCompleter, QComboBox, QPushButton,
    QLabel, QLineEdit, QFormLayout
)

from .CQLWidget import CQLQueryGenerator

class FindWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.CQLQueryGenerator = CQLQueryGenerator(self)
        self.initUI()

    def initUI(self):
        fbox = QFormLayout()

        fbox.addRow(QLabel('Find'))

        self.lineEdit = QLineEdit()
        fbox.addRow(self.lineEdit)

        button = QPushButton('CQL Generator')
        button.clicked.connect(lambda : self.CQLQueryGenerator.show())

        fbox.addRow(button)

        fbox.addRow(QPushButton('Find'))

        fbox.addRow(QLabel('Replace'))
        fbox.addRow(QLineEdit())
        fbox.addRow(QPushButton('Replace'))

        fbox.addRow(QLabel('Matches'))
        fbox.addRow(QLabel('Matched1\nMatched2\nMatched3\nMatched4\n'))

        self.setLayout(fbox)
