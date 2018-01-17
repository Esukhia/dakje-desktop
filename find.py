# PYQT5 PyQt4’s QtGui module has been split into PyQt5’s QtGui, QtPrintSupport and QtWidgets modules


from PyQt5 import QtWidgets

from functools import wraps

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt

import re


class FindDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):

        QtWidgets.QDialog.__init__(self, parent)

        self.parent = parent

        self.lastStart = 0

        self.initUI()

    def initUI(self):

        # Button to search the document for something
        findButton = QtWidgets.QPushButton("Find", self)
        findButton.clicked.connect(self.find)

        # Button to replace the last finding
        replaceButton = QtWidgets.QPushButton("Replace", self)
        replaceButton.clicked.connect(self.replace)

        # Button to remove all findings
        allButton = QtWidgets.QPushButton("Replace all", self)
        allButton.clicked.connect(self.replaceAll)

        # Normal mode - radio button
        self.normalRadio = QtWidgets.QRadioButton("Normal", self)

        # Regular Expression Mode - radio button
        regexRadio = QtWidgets.QRadioButton("RegEx", self)

        # The field into which to type the query
        self.findField = QtWidgets.QPlainTextEdit(self)
        self.findField.resize(250, 50)

        # The field into which to type the text to replace the
        # queried text
        self.replaceField = QtWidgets.QPlainTextEdit(self)
        self.replaceField.resize(250, 50)

        layout = QtWidgets.QGridLayout()

        layout.addWidget(self.findField, 1, 0, 1, 4)
        layout.addWidget(self.normalRadio, 2, 2)
        layout.addWidget(regexRadio, 2, 3)
        layout.addWidget(findButton, 2, 0, 1, 2)

        layout.addWidget(self.replaceField, 3, 0, 1, 4)
        layout.addWidget(replaceButton, 4, 0, 1, 2)
        layout.addWidget(allButton, 4, 2, 1, 2)

        self.setGeometry(300, 300, 360, 250)
        self.setWindowTitle("Find and Replace")
        self.setLayout(layout)

        # By default the normal mode is activated
        self.normalRadio.setChecked(True)

    def find(self):
        self.parent.textEdit.cursorPositionChanged.disconnect()

        # Grab the parent's text
        text = self.parent.textEdit.toPlainText()

        # And the text to find
        query = self.findField.toPlainText()

        if self.normalRadio.isChecked():

            # Use normal string search to find the query from the
            # last starting position
            self.lastStart = text.find(query, self.lastStart + 1)

            # If the find() method didn't return -1 (not found)
            if self.lastStart >= 0:

                end = self.lastStart + len(query)

                self.moveCursor(self.lastStart, end)

            else:

                # Make the next search start from the begining again
                self.lastStart = 0

                self.parent.textEdit.moveCursor(QtGui.QTextCursor.End)

        else:

            # Compile the pattern
            pattern = re.compile(query)

            # The actual search
            match = pattern.search(text, self.lastStart + 1)

            if match:

                self.lastStart = match.start()

                self.moveCursor(self.lastStart, match.end())

            else:

                self.lastStart = 0

                # We set the cursor to the end if the search was unsuccessful
                self.parent.textEdit.moveCursor(QtGui.QTextCursor.End)

        self.parent.textEdit.cursorPositionChanged.connect(
            self.parent.eventHandler.cursorPositionChanged)

    def replace(self, highlight=True):
        self.parent.textEdit.cursorPositionChanged.disconnect()
        self.parent.textEdit.textChanged.disconnect()

        # Grab the text cursor
        cursor = self.parent.textEdit.textCursor()

        # Security
        if cursor.hasSelection():
            for word in self.parent.words:
                if cursor.selectionStart() == word.partOfSpeechStart + 1 and \
                                cursor.selectionEnd() == word.partOfSpeechEnd + 1:
                    word.partOfSpeech = self.replaceField.toPlainText()

            cursor.insertText(self.replaceField.toPlainText())

            # And set the new cursor
            self.parent.textEdit.setTextCursor(cursor)

        self.parent.textEdit.cursorPositionChanged.connect(
            self.parent.cursorIsChanged)
        self.parent.textEdit.textChanged.connect(
            self.parent.textIsChanged)

        if highlight:
            self.parent.highlight()

    def replaceAll(self):
        self.lastStart = 0

        self.find()

        # Replace and find until self.lastStart is 0 again
        while self.lastStart:
            self.replace(highlight=False)
            self.find()

        self.parent.highlight()

    def moveCursor(self, start, end):
        # We retrieve the QTextCursor object from the parent's QPlainTextEdit
        cursor = self.parent.textEdit.textCursor()

        # Then we set the position to the beginning of the last match
        cursor.setPosition(start)

        # Next we move the Cursor by over the match and pass the KeepAnchor parameter
        # which will make the cursor select the the match's text
        cursor.movePosition(QtGui.QTextCursor.Right,
                            QtGui.QTextCursor.KeepAnchor, end - start)

        # And finally we set this new cursor as the parent's 
        self.parent.textEdit.setTextCursor(cursor)
