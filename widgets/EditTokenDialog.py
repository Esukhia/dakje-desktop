import os
import json

from PyQt5 import QtCore, QtWidgets, QtGui

from pybo import Token as PyboToken

from storage.models import Rule
from storage.models import Token as TokenModel
from storage.settings import BASE_DIR
from .CQLWidget import CqlQueryGenerator


class CqlHBox(QtWidgets.QHBoxLayout):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        # previous
        self.previousCql = QtWidgets.QLineEdit()
        self.addWidget(self.previousCql)

        # generator
        self.cqlQueryGenerator = CqlQueryGenerator(self.previousCql)
        self.cqlQueryGeneratorBtn = QtWidgets.QPushButton()
        self.cqlQueryGeneratorBtn.setFlat(True)
        self.cqlQueryGeneratorBtn.setIcon(QtGui.QIcon(os.path.join(BASE_DIR, "icons", "CQL.png")))
        self.cqlQueryGeneratorBtn.setIconSize(QtCore.QSize(16, 16))
        self.cqlQueryGeneratorBtn.clicked.connect(lambda: self.cqlQueryGenerator.show())
        self.addWidget(self.cqlQueryGeneratorBtn)

        self.tokenCqlLabel = QtWidgets.QLabel()
        self.attrCql = QtWidgets.QLineEdit()
        self.addWidget(self.tokenCqlLabel)
        self.addWidget(self.attrCql)
        self.addWidget(QtWidgets.QLabel(']'))

        # next
        self.nextCql = QtWidgets.QLineEdit()
        self.addWidget(self.nextCql)

        # generator
        self.cqlQueryGenerator2 = CqlQueryGenerator(self.nextCql)
        self.cqlQueryGeneratorBtn2 = QtWidgets.QPushButton()
        self.cqlQueryGeneratorBtn2.setFlat(True)
        self.cqlQueryGeneratorBtn2.setIcon(QtGui.QIcon(os.path.join(BASE_DIR, "icons", "CQL.png")))
        self.cqlQueryGeneratorBtn2.setIconSize(QtCore.QSize(16, 16))
        self.cqlQueryGeneratorBtn2.clicked.connect(lambda: self.cqlQueryGenerator2.show())
        self.addWidget(self.cqlQueryGeneratorBtn2)

        # delete
        self.deleteBtn = QtWidgets.QPushButton()
        self.deleteBtn.setFlat(True)
        self.deleteBtn.setIcon(QtGui.QIcon(os.path.join(BASE_DIR, "icons", "delete.png")))
        self.deleteBtn.setIconSize(QtCore.QSize(30, 30))
        self.deleteBtn.clicked.connect(self.removeLayout)
        self.addWidget(self.deleteBtn)

    def setToken(self, token):
        self.content = token.content
        self.tokenCqlLabel.setText('[content="{}"'.format(token.content))

    def getCql(self):
        return self.previousCql.text() + \
               self.getActionCql() + self.nextCql.text()

    def getActionCql(self):
        return self.tokenCqlLabel.text() + self.attrCql.text() + ']'

    def isBlank(self):
        if (self.previousCql.text() == '' and
            self.attrCql.text() == '' and
                self.nextCql.text() == ''):
            return True
        else:
            return False

    def removeLayout(self):
        self.parent.ruleBoxes.remove(self)
        for i in reversed(range(self.count())):
            self.itemAt(i).widget().setParent(None)
        self.setParent(None)


class HistoryHBox(QtWidgets.QHBoxLayout):
    def __init__(self, rule, parent):
        super().__init__()

        self.rule = rule
        self.parent = parent

        self.deleteBtn = QtWidgets.QPushButton()
        self.deleteBtn.setFlat(True)
        self.deleteBtn.setIcon(QtGui.QIcon(os.path.join(BASE_DIR, "icons", "delete.png")))
        self.deleteBtn.setIconSize(QtCore.QSize(30, 30))
        self.deleteBtn.clicked.connect(self.delete)

        self.addWidget(QtWidgets.QLabel(self.rule.cql))
        self.addStretch(1)
        self.addWidget(self.deleteBtn)

    def delete(self):
        self.rule.delete()
        self.removeLayout()

    def removeLayout(self):
        self.itemAt(2).widget().setParent(None)
        self.itemAt(0).widget().setParent(None)
        self.setParent(None)


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
        # Add Rule Button & Confirm
        self.ruleLabel = QtWidgets.QLabel('Rule')
        self.addRuleButton = QtWidgets.QPushButton()
        self.addRuleButton.setFlat(True)
        self.addRuleButton.setIcon(QtGui.QIcon(os.path.join(BASE_DIR, "icons", "add.png")))
        self.addRuleButton.setIconSize(QtCore.QSize(30, 30))
        self.addRuleButton.clicked.connect(self.addRuleBox)

        self.ruleHBox = QtWidgets.QHBoxLayout()
        self.ruleHBox.addWidget(self.ruleLabel)
        self.ruleHBox.addStretch(1)
        self.ruleHBox.addWidget(self.addRuleButton)
        self.fbox.addRow(self.ruleHBox)

        self.historyVBox = QtWidgets.QVBoxLayout(self)
        self.fbox.addRow(QtWidgets.QLabel('Existing Rules'))
        self.fbox.addRow(self.historyVBox)

        # confirm
        self.confirmButton = QtWidgets.QPushButton()
        self.confirmButton.setText('Confirm')
        self.confirmButton.clicked.connect(self.confirm)
        self.fbox.addRow(self.confirmButton)
        self.setLayout(self.fbox)

    def addRuleBox(self):
        newRuleBox = CqlHBox(self)
        newRuleBox.setToken(self.token)
        row = self.fbox.rowCount() - 3
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

        for i in reversed(range(self.historyVBox.count())):
            self.historyVBox.itemAt(i).removeLayout()

        for rule in Rule.objects.filter(actionCql__icontains=token.content):
            self.historyVBox.addLayout(HistoryHBox(rule, self))

        self.addRuleBox()

    def setSecondToken(self, token):
        self.secondToken = token

    def setMode(self, mode):
        self.mode = mode

    def setAddingIndex(self, index):
        self.addingIndex = index

    def confirm(self):
        if self.mode == self.MODE_UPDATE:
            ok = self.updateToken()

            if ok == False:
                return
        else:
            self.addToken()

        self.editor.refreshView()
        self.close()

    def updateToken(self):
        data = {
            'pos': self.posField.text(),
            'lemma': self.lemmaField.text(),
            'meaning': self.meaningField.toPlainText()
        }

        if self.levelField.text() != '':
            data['level'] = int(self.levelField.text())

        if all(ruleBox.isBlank() for ruleBox in self.ruleBoxes):
            response = QtWidgets.QMessageBox.warning(
                self, 'Blank CQL Warning',
                'If there is no cql queries, the attributes '
                'will be applied under normal circumstances.',
                buttons=QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel
            )
            if response == QtWidgets.QMessageBox.Cancel:
                return False

            tokenModel = TokenModel.objects.get_or_create(
                content=self.token.content, type=TokenModel.TYPE_UPDATE)[0]
            tokenModel.pos = data.get('pos')
            tokenModel.lemma = data.get('lemma')
            tokenModel.meaning = data.get('meaning')
            tokenModel.level = data.get('level')
            tokenModel.save()

            # add to trie
            self.editor.bt.inflect_n_add(
                tokenModel.content, tokenModel.pos, 'data')
            self.editor.resegment()
        else:
            for ruleBox in self.ruleBoxes:
                if not ruleBox.isBlank():
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
            TokenModel.objects.get_or_create(
                content=self.token.content + self.secondToken.content,
                action=TokenModel.TYPE_REMOVE)

        # add the token to trie & dict
        self.editor.bt.add(token.content)
        tokenModel = TokenModel.objects.get_or_create(
            content=token.content, action=TokenModel.TYPE_UPDATE)[0]
        tokenModel.pos = token.pos
        tokenModel.save()

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
