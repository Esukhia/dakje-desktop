import sys

from functools import partial

from PyQt5.QtCore import Qt, QStringListModel, QSize
from PyQt5.QtGui import QTextCursor, QPalette, QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QWidget, QTextEdit, QCompleter, QComboBox, QPushButton, QMainWindow,
    QLabel, QLineEdit, QFormLayout, QHBoxLayout, QVBoxLayout, QDialog
)

class RemoveButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlat(True)
        self.setIconSize(QSize(20, 20))
        self.setIcon(QIcon('files/delete.png'))
        self.setFixedSize(20, 20)

class ComboBoxFactory:
    KEYWORD = ['WORD', 'LEMMA', 'POS', 'TAG']
    RELATIONAL_OPR = ['=', '>', '<']
    LOGICAL_OPR = ['', '&', '|']

    @staticmethod
    def createComboBox(items):
        comboBox = QComboBox()
        comboBox.addItems(items)
        return comboBox

class Condition:
    def __init__(self, parent=None):
        self.parent = parent

        # Keyword
        self.keywordField = ComboBoxFactory.createComboBox(
            ComboBoxFactory.KEYWORD)
        self.keywordField.setEditable(True)
        self.keywordField.currentIndexChanged.connect(self.generateQuery)
        self.keywordField.currentTextChanged.connect(self.generateQuery)

        # Value
        self.valueField = QLineEdit()
        self.valueField.textChanged.connect(self.generateQuery)

        # Rational Operator
        self.rationalOperatorField = ComboBoxFactory.createComboBox(
            ComboBoxFactory.RELATIONAL_OPR)
        self.rationalOperatorField.setEditable(True)
        self.rationalOperatorField.currentIndexChanged.connect(
            self.generateQuery)
        self.rationalOperatorField.currentTextChanged.connect(self.generateQuery)

        # Logical Operator
        self.logicalOperatorField = ComboBoxFactory.createComboBox(
            ComboBoxFactory.LOGICAL_OPR)
        self.logicalOperatorField.setEditable(True)
        self.logicalOperatorField.currentIndexChanged.connect(
            self.generateQuery)
        self.logicalOperatorField.currentTextChanged.connect(self.generateQuery)

        # Remove
        self.removeButton = RemoveButton()
        self.removeButton.clicked.connect(self.remove)

        # Layout
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.keywordField)
        self.hbox.addWidget(self.rationalOperatorField)
        self.hbox.addWidget(self.valueField)
        self.hbox.addWidget(self.logicalOperatorField)
        self.hbox.addWidget(self.removeButton)

        # Widget
        self.widget = QWidget()
        self.widget.setLayout(self.hbox)

    @property
    def keyword(self):
        return self.keywordField.currentText()

    @property
    def value(self):
        return self.valueField.text()

    @property
    def rationalOperator(self):
        return self.rationalOperatorField.currentText()

    @property
    def logicalOperator(self):
        return self.logicalOperatorField.currentText()

    def generateQuery(self):
        self.parent.generateQuery()

    def remove(self):
        self.keywordField.setParent(None)
        self.rationalOperatorField.setParent(None)
        self.valueField.setParent(None)
        self.logicalOperatorField.setParent(None)
        self.removeButton.setParent(None)
        self.widget.setParent(None)

        self.parent.conditions.remove(self)
        self.generateQuery()

    def __str__(self):
        result = '{}{}"{}"'.format(
            self.keyword, self.rationalOperator, self.value)

        if self.logicalOperator:
            result += ' {} '.format(self.logicalOperator)
        return result


class Token:
    def __init__(self, parent):
        self.parent = parent
        self.conditions = []

        self.removeButton = RemoveButton()
        self.removeButton.clicked.connect(self.remove)

        self.addConditionButton = QPushButton('Add Condition')
        self.addConditionButton.clicked.connect(self.addCondition)

        self.fbox = QFormLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.removeButton)
        hbox.addWidget(self.addConditionButton)
        self.fbox.addRow(hbox)

        self.widget = QWidget()
        self.widget.setLayout(self.fbox)
        # self.widget.setStyleSheet('background-color: white')
        # self.widget.autoFillBackground()

    def addCondition(self):
        self.conditions.append(Condition(parent=self))
        self.fbox.addRow(self.conditions[-1].widget)
        self.generateQuery()

    def removeAttribute(self, condition):
        self.generateQuery()

    def generateQuery(self):
        self.parent.generateQuery()

    def remove(self):
        for condition in reversed(self.conditions):
            condition.remove()
        self.removeButton.setParent(None)
        self.addConditionButton.setParent(None)
        self.widget.setParent(None)

        self.parent.tokens.remove(self)
        self.generateQuery()

    def __str__(self):
        token = '[{}]'
        conditions = ''.join([str(condition) for condition in self.conditions])
        return token.format(conditions)


class CQLQueryGenerator(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.tokens = []
        self.resize(450, 600)
        self.initUI()

    def initUI(self):
        self.CQLQueryLabel = QLabel('CQL Query String')
        self.CQLQueryLabel.setStyleSheet('background-color: white')

        self.addTokenButton = QPushButton('Add Token')
        self.addTokenButton.clicked.connect(self.addToken)

        self.confirmButton = QPushButton('Confirm')
        self.confirmButton.clicked.connect(self.confirm)

        self.fbox = QFormLayout()
        self.fbox.addRow(self.CQLQueryLabel)

        hbox = QHBoxLayout()
        hbox.addWidget(self.addTokenButton)
        hbox.addWidget(self.confirmButton)
        self.fbox.addRow(hbox)

        self.setLayout(self.fbox)

    def addToken(self):
        self.tokens.append(Token(parent=self))
        self.fbox.addRow(self.tokens[-1].widget)

        for condition in self.tokens[-1].conditions:
            condition.keywordField.currentIndexChanged.connect(
                self.generateQuery)

        self.generateQuery()

    def removeToken(self, token):
        self.generateQuery()

    def generateQuery(self):
        self.CQLQueryLabel.setText(str(self))

    def confirm(self):
        self.parent.lineEdit.setText(str(self))
        self.close()

    def __str__(self):
        return ''.join([str(token) for token in self.tokens])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setCentralWidget(CQLQueryGenerator())
    window.show()
    app.exec()
