from PyQt5 import QtGui, QtCore, QtWidgets

class WordCount(QtWidgets.QDialog):
    def __init__(self,parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
    # Total word count
        totalLabel = QtGui.QLabel("Total",self)
        totalLabel.setStyleSheet("font-weight:bold; font-size: 15px;")

        totalWordsLabel = QtGui.QLabel("Words: ", self)

        self.totalWords = QtGui.QLabel(self)

    def getText(self):
        text = self.parent.text.toPlainText()
        words = str(len(text.split()))
        self.totalWords.setText(words)