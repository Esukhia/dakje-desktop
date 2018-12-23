import json

from PyQt5 import QtCore, QtWidgets

from storage.models import Rule

class EditTokenDialog(QtWidgets.QDialog):
    def __init__(self, editor=None):
        super().__init__(parent=editor)
        self.editor = editor
        self.initForm()
        self.setWindowTitle("Edit Token...")
        self.setStyleSheet("background-color: white; width: 150px;")

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

        # Rule
        self.ruleBox = QtWidgets.QHBoxLayout()

        # previous
        self.previousCql = QtWidgets.QLineEdit()
        self.ruleBox.addWidget(self.previousCql)

        self.tokenCqlLabel = QtWidgets.QLabel()
        self.attrCql = QtWidgets.QLineEdit()
        self.ruleBox.addWidget(self.tokenCqlLabel)
        self.ruleBox.addWidget(self.attrCql)
        self.ruleBox.addWidget(QtWidgets.QLabel(']'))

        # next
        self.nextCql = QtWidgets.QLineEdit()
        self.ruleBox.addWidget(self.nextCql)

        self.fbox.addRow("Rule", self.ruleBox)

        # Confirm
        self.confirmButton = QtWidgets.QPushButton()
        self.confirmButton.setText('Confirm')
        self.confirmButton.clicked.connect(self.confirm)
        self.fbox.addRow(self.confirmButton)

        self.setLayout(self.fbox)

    def setToken(self, token):
        self.token = token
        self.contentLabel.setText(token.content)
        self.tokenCqlLabel.setText('[content=' + token.content)
        self.posField.setText(token.pos)
        self.lemmaField.setText(token.lemma)
        self.levelField.setText(str(token.level))

    def confirm(self):
        data = {
            'pos': self.posField.text(),
            'lemma': self.lemmaField.text(),
            'level': int(self.levelField.text())
        }

        actionCql = self.tokenCqlLabel.text() + self.attrCql.text() + ']'
        cql = self.previousCql.text() + actionCql + self.nextCql.text()

        Rule.objects.create(
            cql=cql,
            actionCql=actionCql,
            action=json.dumps(data),
            type='U',
            order=1
        )

        self.editor.refreshView()
        self.editor.refreshCoverage()
        self.close()
