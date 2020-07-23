from PyQt5 import QtGui, QtCore, QtWidgets
from django.utils.translation import gettext_lazy as _

# Total word count
class WordCount(QtWidgets.QDialog):
    def __init__(self,parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        totalLabel = QtGui.QLabel(str(_("Total")),self)
        totalLabel.setStyleSheet("font-weight:bold; font-size: 15px;")

        totalWordsLabel = QtGui.QLabel(_("Words: "), self)

        self.totalWords = QtGui.QLabel(self)

    def getText(self):
        text = self.parent.text.toPlainText()
        words = str(len(text.split()))
        self.totalWords.setText(words)
