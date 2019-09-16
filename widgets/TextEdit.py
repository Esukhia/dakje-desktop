import copy

from PyQt5 import QtCore, QtGui, QtWidgets

class TextEdit(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filename = None

    @property
    def editor(self):
        return self.parent().parent()

    def newFile(self):
        self.clear()

    def openFile(self):
        self.filename, ok = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open File', ".", "UTF-8 (*.txt)")

        if self.filename:
            with open(self.filename, "r", encoding='utf-8') as f:
                self.setPlainText(f.read())

    def saveFile(self):
        if not self.filename:
            self.filename, ok = QtWidgets.QFileDialog.getSaveFileName(
                self, "Choose a file name", '.', "UTF-8 (*.txt)")

            if not ok:
                return

        if not self.filename:
            return

        writer = QtGui.QTextDocumentWriter(self.filename)
        success = writer.write(self.document())

        if success:
            return self.filename
        else:
            QtWidgets.QMessageBox.question(
                self, 'Cancel', 'Saving Failed', QtWidgets.QMessageBox.Yes)

    def undo(self):
        self.document().undo()

    def redo(self):
        self.document().redo()

    def keyPressEvent(self, e):
        from widgets.EditTokenDialog import EditTokenDialog

        if self.editor.viewManager.isSpaceView():

            if self.textCursor().hasSelection():
                QtWidgets.QMessageBox.warning(
                    self, 'Mode Error',
                    'Please dont edit text in space mode.'
                    'Users can only split/merge tokens in this mode',
                    buttons=QtWidgets.QMessageBox.Ok
                )
                return

            # split token
            # TODO any key becomes space? maybe just tsek and space
            if e.key() == QtCore.Qt.Key_Space:
                position = self.textCursor().position()  # before pressing
                index, token = self.editor.tokenManager.find(position)
                del self.editor.tokens[index]

                tokenLeft = copy.deepcopy(token)
                tokenLeft.content = token.content[:position - token.start]

                tokenRight = copy.deepcopy(token)
                tokenRight.content = token.content[position - token.start:]

                self.editor.editTokenDialog.setMode(EditTokenDialog.MODE_ADD_2)
                self.editor.editTokenDialog.setAddingIndex(index)
                self.editor.editTokenDialog.setToken(tokenLeft)
                self.editor.editTokenDialog.setSecondToken(tokenRight)
                self.editor.editTokenDialog.show()

            # merge tokens
            elif e.key() == QtCore.Qt.Key_Backspace:
                position = self.textCursor().position()  # before pressing
                indexLeft, tokenLeft = self.editor.tokenManager.find(position - 2)
                indexRight, tokenRight = self.editor.tokenManager.find(position)
                del self.editor.tokens[indexLeft:indexRight + 1]

                newToken = copy.deepcopy(tokenLeft)
                newToken.content = tokenLeft.content + tokenRight.content

                self.editor.editTokenDialog.setMode(EditTokenDialog.MODE_ADD)
                self.editor.editTokenDialog.setAddingIndex(indexLeft)
                self.editor.editTokenDialog.setToken(newToken)
                self.editor.editTokenDialog.show()

        super().keyPressEvent(e)

    def setTokensSelection(self, tokenIndexStart, tokenIndexEnd):
        tokens = self.editor.tokens
        self.setSelection(tokens[tokenIndexStart].start,
                          tokens[tokenIndexEnd].end)

    def setSelection(self, start, end):
        cursor = self.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QtGui.QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)
