import copy

from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTextEdit, QUndoCommand, QUndoStack

from web.settings import DESKTOP


class EmulatedTextUndoCommand(QUndoCommand):

    def __init__(self, edit, oldText, newText,
                 oldCursorPosition=None, newCursorPosition=None):
        super(EmulatedTextUndoCommand, self).__init__("")
        self.edit = edit
        self.oldText = oldText
        self.newText = newText
        self.oldCursorPosition = oldCursorPosition
        self.newCursorPosition = newCursorPosition

        self.called = False

    def redo(self):
        if not self.called:
            self.called = True
            return

        print("redo: %s" % self)
        self.edit._setPlainText(self.newText)
        if self.newCursorPosition:
            print("redo cursor position: %d" % self.newCursorPosition)
            self.edit.blockSignals(True)
            try:
                t = self.edit.textCursor()
                t.setPosition(self.newCursorPosition)
                self.edit.setTextCursor(t)
            finally:
                self.edit.blockSignals(False)

    def undo(self):
        print("undo: %s" % self)
        self.edit._setPlainText(self.oldText)
        if self.oldCursorPosition:
            print("undo cursor position: %d" % self.oldCursorPosition)
            self.edit.blockSignals(True)
            try:
                t = self.edit.textCursor()
                t.setPosition(self.oldCursorPosition)
                self.edit.setTextCursor(t)
            finally:
                self.edit.blockSignals(False)

    def __str__(self, *args, **kwargs):
        return "old: %s, new: %s" % (self.oldText, self.newText)


class CustomUndoTextEdit(QTextEdit):
    def __init__(self, *args, undoStack=None, **kws):
        super().__init__(*args, **kws)

        self.undoStack = (undoStack if undoStack is not None
                          else QUndoStack(self))
        self.textChangedAfterUndoCommandAdded = False

        self.document().undoCommandAdded.connect(
            self.onUndoCommandAdded)
        self.textChanged.connect(self.onTextChanged)

    def _setPlainText(self, text):
        self.blockSignals(True)
        try:
            return QTextEdit.setPlainText(self, text)
        finally:
            self.blockSignals(False)

    def setPlainText(self, text):
        command = EmulatedTextUndoCommand(self,
            self.toPlainText(), text,
                self.textCursor().position(),
                self.textCursor().position())
        self.undoStack.push(command)

        result = QTextEdit.setPlainText(self, text)
        self.textChangedAfterUndoCommandAdded = False
        return result

    def keyPressEvent(self, event):
        # print("keyPressEvent")

        # only allow to add spaces and delete in SpaceView
        if self.editor.viewManager.isSpaceView():
            if event.key() != (Qt.Key_Space or Qt.Key_Backspace):
                return
            else:
                QTextEdit.keyPressEvent(self, event)

        else:
            if event.key() == (Qt.Key_Control and Qt.Key_Z):
                print("press Undo")
                self.undo()
            elif event.key() == (Qt.Key_Control and Qt.Key_Y):
                print("press Redo")
                self.redo()
            else: # call base class keyPressEvent
                QTextEdit.keyPressEvent(self, event)

    def onTextChanged(self):
        print("onTextChanged")
        self.textChangedAfterUndoCommandAdded = True

    def onUndoCommandAdded(self):
        print("insert undo command: %s %d" % (
            self.toPlainText(), self.textCursor().position()))
        if self.undoStack.isClean():
            command = EmulatedTextUndoCommand(
                self, "", self.toPlainText(),
                None, self.textCursor().position())
        else:
            lastCommand = self.undoStack.command(self.undoStack.count() - 1)
            command = EmulatedTextUndoCommand(
                self, lastCommand.newText, self.toPlainText(),
                lastCommand.newCursorPosition,
                self.textCursor().position())
        self.undoStack.push(command)
        self.textChangedAfterUndoCommandAdded = False

    def undo(self):
        print("undo")
        if self.textChangedAfterUndoCommandAdded:
            lastCommand = self.undoStack.command(self.undoStack.count() - 1)
            command = EmulatedTextUndoCommand(
                self, lastCommand.newText, self.toPlainText(),
                lastCommand.newCursorPosition,
                self.textCursor().position())
            self.undoStack.push(command)

        self.undoStack.undo()
        self.textChangedAfterUndoCommandAdded = False

    def redo(self):
        print("redo")
        self.undoStack.redo()
        self.textChangedAfterUndoCommandAdded = False

    # Paste without formatting
    def insertFromMimeData(self, source):
        self.insertPlainText(source.text())


class TextEdit(CustomUndoTextEdit):
    def __init__(self, parent=None, *args, **kws):
        super().__init__(parent, *args, **kws)
        self.filename = None

    @property
    def editor(self):
        return self.parent().parent()

    def newFile(self):
        self.clear()

    def openFile(self):
        self.filename, ok = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open File', DESKTOP, "UTF-8 (*.txt)")

        if self.filename:
            with open(self.filename, "r", encoding='utf-8') as f:
                self.setPlainText(f.read())

    def saveFile(self):
        if not self.filename:
            self.filename, ok = QtWidgets.QFileDialog.getSaveFileName(
                self, "Choose a file name", DESKTOP, "UTF-8 (*.txt)")

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


    def keyPressEvent(self, e):
        from widgets.EditTokenDialog import EditTokenDialog

        # if self.editor.viewManager.isPlainTextView():
        #     print("entered in here")
        #     # if e.key() == QtCore.Qt.Key_Backspace:
        #     #     print("entered in backspace")
        #     #     self.editor.segment()

        if self.editor.viewManager.isSpaceView():
            # if self.textCursor().hasSelection():
            #     QtWidgets.QMessageBox.warning(
            #         self, 'Mode Error',
            #         'Please dont edit text in space mode.'
            #         'Users can only split/merge tokens in this mode',
            #         buttons=QtWidgets.QMessageBox.Ok
            #     )
            #     return

            # split token
            # TODO any key becomes space? maybe just tsek and space
            if e.key() == QtCore.Qt.Key_Space:
                position = self.textCursor().position()  # before pressing
                index, token = self.editor.tokenManager.find(position)
                del self.editor.tokens[index]

                tokenLeft = copy.deepcopy(token)
                tokenLeft.text = token.text[:position - token.start]

                tokenRight = copy.deepcopy(token)
                tokenRight.text = token.text[position - token.start:]

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
                # TODO take care of other attributes
                newToken.text = tokenLeft.text + tokenRight.text
                newToken.lemma = newToken.text

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
