
from PyQt5.QtWidgets import (
    QWidget, QTabWidget, QFormLayout, QHBoxLayout, QVBoxLayout,
    QColorDialog, QFileDialog, QInputDialog, QLabel, QPushButton
)

class CounterWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.formLayout = QFormLayout()

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Name'))
        hbox.addWidget(QLabel('Number'))

        self.formLayout.addRow(hbox)
        self.setLayout(self.formLayout)

    def addTextFormat(self, textFormat):
        textFormat.counterNameLabel = QLabel(textFormat.name)
        textFormat.counterLabel = QLabel(str(len(textFormat.wordList)))
        hbox = QHBoxLayout()
        hbox.addWidget(textFormat.counterNameLabel)
        hbox.addWidget(textFormat.counterLabel)
        textFormat.counterHBox = hbox
        self.formLayout.addRow(hbox)

    def removeTextFormat(self, textFormat):
        for i in reversed(range(textFormat.counterHBox.count())):
            textFormat.counterHBox.itemAt(i).widget().setParent(None)

        self.formLayout.removeItem(textFormat.counterHBox)

    def refresh(self):
        for textFormat in self.parent.textFormatManager.getFormats():
            textFormat.counterLabel.setText(str(textFormat.counter))
