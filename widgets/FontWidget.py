from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication, QFontDialog, QMainWindow, QLabel, QTextEdit, QVBoxLayout, QAction

import sys

class App(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.title = 'Text Editor'
        self.left = 10
        self.top = 10
        self.width = 1080
        self.height = 920

        self.widget = QWidget(self)
        self.lbl    = QLabel(self)

        self.text = QTextEdit(self.widget)
        self.widget.setLayout(QVBoxLayout())
        self.widget.layout().addWidget(self.text)
        self.setCentralWidget(self.widget)
        self.initUI()



    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        toolBar = self.menuBar()
        fileMenu = toolBar.addMenu('File')
        editMenu = toolBar.addMenu('Edit')
        toolsMenu = toolBar.addMenu('Tools')
        helpMenu = toolBar.addMenu('Help')

        fontButton = QAction('Configure Editor', self)
        fontButton.setShortcut('Ctrl+E')
        fontButton.triggered.connect(self.font_set)
        toolsMenu.addAction(fontButton)



    def font_set(self):
        font, ok = QFontDialog.getFont(self.text.font(), self)
        if ok:
            self.text.setFont(font)
            print("Display Fonts", font)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())