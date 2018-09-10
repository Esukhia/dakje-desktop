from PyQt5 import QtCore, QtGui, QtWidgets

class TextEdit(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filename = None

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
