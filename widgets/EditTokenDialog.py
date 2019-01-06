import json

from PyQt5 import QtCore, QtWidgets, QtGui

from pybo import Token as PyboToken

from storage.models import Rule, Dict

class CqlHBox(QtWidgets.QHBoxLayout):
    def __init__(self):
        super().__init__()

        # previous
        self.previousCql = QtWidgets.QLineEdit()
        self.addWidget(self.previousCql)

        self.tokenCqlLabel = QtWidgets.QLabel()
        self.attrCql = QtWidgets.QLineEdit()
        self.addWidget(self.tokenCqlLabel)
        self.addWidget(self.attrCql)
        self.addWidget(QtWidgets.QLabel(']'))

        # next
        self.nextCql = QtWidgets.QLineEdit()
        self.addWidget(self.nextCql)

    def setToken(self, token):
        self.tokenCqlLabel.setText('[content="{}"'.format(token.content))

    def getCql(self):
        return self.previousCql.text() + \
               self.getActionCql() + self.nextCql.text()

    def getActionCql(self):
        return self.tokenCqlLabel.text() + self.attrCql.text() + ']'


class EditTokenDialog(QtWidgets.QDialog):
    MODE_ADD = 1
    MODE_ADD_2 = 2
    MODE_UPDATE = 3

    def __init__(self, editor=None):
        super().__init__(parent=editor)
        self.editor = editor
        self.mode = self.MODE_UPDATE
        self.ruleBoxes = []
        self.token = None
        self.secondToken = None
        self.initForm()
        self.setWindowTitle("Edit Token...")
        self.setStyleSheet("QDialog{background-color: white; width: 150px;}")

    def initForm(self):
        self.fbox = QtWidgets.QFormLayout(self)

        # Content
        self.contentLabel = QtWidgets.QLabel()
        self.fbox.addRow(self.contentLabel)

        # POS
        self.posField = QtWidgets.QLineEdit()
        self.fbox.addRow("POS", self.posField)

        # Lemma
        self.lemmaField = QtWidgets.QLineEdit()
        self.fbox.addRow("Lemma", self.lemmaField)

        # Level
        # TODO: Change Field To Number Type
        self.levelField = QtWidgets.QLineEdit()
        self.fbox.addRow("Level", self.levelField)

        # Meaning
        self.meaningField = QtWidgets.QTextEdit()
        self.meaningField.setFixedHeight(
            self.meaningField.fontMetrics().lineSpacing() * 3)  # 3 rows
        self.fbox.addRow("Meaning", self.meaningField)

        # Rule
        self.fbox.addRow(QtWidgets.QLabel('Rule'))

        # Add Rule Button & Confirm
        self.addRuleButton = QtWidgets.QPushButton()
        self.addRuleButton.setFlat(True)
        self.addRuleButton.setIcon(QtGui.QIcon('icons/add.png'))
        self.addRuleButton.setIconSize(QtCore.QSize(30, 30))
        self.addRuleButton.clicked.connect(self.addRuleBox)

        self.confirmButton = QtWidgets.QPushButton()
        self.confirmButton.setText('Confirm')
        self.confirmButton.clicked.connect(self.confirm)
        self.fbox.addRow(self.addRuleButton, self.confirmButton)

        self.setLayout(self.fbox)

    def addRuleBox(self):
        newRuleBox = CqlHBox()
        newRuleBox.setToken(self.token)
        row = self.fbox.rowCount() - 1
        self.fbox.insertRow(row, newRuleBox)
        self.ruleBoxes.append(newRuleBox)

    def setToken(self, token):
        self.token = token
        self.contentLabel.setText(token.content)
        self.posField.setText(token.pos)
        self.lemmaField.setText(token.lemma)
        self.levelField.setText('')
        self.meaningField.setText('')

        if token.level is not None:
            self.levelField.setText(str(token.level))

        if token.meaning is not None:
            self.meaningField.setText(token.meaning)

        self.addRuleBox()

    def setSecondToken(self, token):
        self.secondToken = token

    def setMode(self, mode):
        self.mode = mode

    def setAddingIndex(self, index):
        self.addingIndex = index

    def confirm(self):
        if self.mode == self.MODE_UPDATE:
            self.updateToken()
        else:
            self.addToken()

        self.editor.refreshView()
        self.editor.refreshCoverage()
        self.close()

    def updateToken(self):
        data = {
            'pos': self.posField.text(),
            'lemma': self.lemmaField.text(),
            'meaning': self.meaningField.toPlainText()
        }

        if self.levelField.text() != '':
            data['level'] = int(self.levelField.text())

        for ruleBox in self.ruleBoxes:
            actionCql = ruleBox.getActionCql()
            cql = ruleBox.getCql()

            Rule.objects.get_or_create(
                cql=cql,
                actionCql=actionCql,
                action=json.dumps(data),
                type=Rule.TYPE_UPDATE,
                order=1
            )

    def addToken(self):
        from managers import Token

        pyboToken = PyboToken()
        pyboToken.content = self.contentLabel.text()
        pyboToken.pos = self.posField.text()
        pyboToken.lemma = self.lemmaField.text()

        token = Token(pyboToken)
        if self.levelField.text() != '':
            token.level = int(self.levelField.text())
        token.meaning = self.meaningField.toPlainText()

        self.editor.tokens.insert(self.addingIndex, token)

        # deactivate the token which hasn't be split
        if self.mode == self.MODE_ADD_2 and self.secondToken:
            self.editor.bt.deactivate_word(
                self.token.content + self.secondToken.content)
            Dict.objects.get_or_create(
                content=self.token.content + self.secondToken.content,
                action=Dict.ACTION_DELETE)

        self.editor.bt.add(token.content)

        dict = Dict.objects.get_or_create(content=token.content,
                                          action=Dict.ACTION_ADD)[0]
        dict.pos = token.pos
        dict.save()

    def reject(self):
        for ruleBox in self.ruleBoxes:
            self.fbox.removeRow(ruleBox)
        self.ruleBoxes = []

        super().reject()

    def close(self):
        for ruleBox in self.ruleBoxes:
            self.fbox.removeRow(ruleBox)
        self.ruleBoxes = []

        super().close()

        if self.mode == self.MODE_ADD_2 and self.secondToken:
            self.setToken(self.secondToken)
            self.setAddingIndex(self.addingIndex + 1)
            self.setSecondToken(None)
            self.show()
