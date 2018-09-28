import sys

from PyQt5 import QtCore, QtWidgets, QtGui

from widgets import MenuBar, ToolBar, CentralWidget
from managers import ActionManager, TokenManager, ViewManager


class ExceptionHandler(QtCore.QObject):
    errorSignal = QtCore.pyqtSignal()

    def __init__(self):
        super(ExceptionHandler, self).__init__()

    def handler(self, exctype, value, traceback):
        self.errorSignal.emit()
        sys._excepthook(exctype, value, traceback)

exceptionHandler = ExceptionHandler()
sys._excepthook = sys.excepthook
sys.excepthook = exceptionHandler.handler


class Editor(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initProperties()
        self.initManagers()
        self.initUI()
        self.setWindowTitle("Tibetan Editor")
        self.setWindowState(QtCore.Qt.WindowMaximized)

    def initProperties(self):
        self.tokens = []
        self.mode = None
        self.view = None
        self.filename = None

    def initManagers(self):
        self.actionManager = ActionManager(self)
        self.tokenManager = TokenManager(self)
        self.viewManager = ViewManager(self)

    def initUI(self):
        self.actionManager.createActions()

        self.menuBar = MenuBar(self.actionManager, parent=self)
        self.setMenuBar(self.menuBar)

        self.toolBar = ToolBar(self.actionManager, parent=self)
        self.addToolBar(self.toolBar)

        self.statusBar = QtWidgets.QStatusBar(parent=self)
        self.setStatusBar(self.statusBar)
        self.statusBar.setStyleSheet('background-color: #EAEAEA')
        self.statusBar.showMessage('Welcome...', 3000)

        self.centralWidget = CentralWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.setStyleSheet('QMainWindow{background-color: white}')
        self.textEdit.setStyleSheet(
            'border: none; font-size: 20px; margin: 10px;')

    @property
    def textEdit(self):
        return self.centralWidget.textEdit

    def toggleSpaceView(self):
        self.segment()
        self.viewManager.toggleSpaceView()
        self.refreshView()

    def toggleTagView(self):
        self.segment()
        self.viewManager.toggleTagView()
        self.refreshView()

    def refreshView(self):
        text = self.tokenManager.getString(self.tokens)
        self.textEdit.setPlainText(text)

    def segment(self):
        if self.tokens:
            return
        text = self.centralWidget.textEdit.toPlainText()
        tokens = self.tokenManager.segment(text)
        self.tokens.extend(tokens)

    ### TextEdit Actions ###

    def newFile(self):
        self.textEdit.newFile()

    def openFile(self):
        self.textEdit.openFile()

    def saveFile(self):
        self.filename = self.textEdit.saveFile()

    def undo(self):
        self.textEdit.undo()

    def redo(self):
        self.textEdit.redo()

    ### TextEdit Actions End ###

    def editToken(self):
        self.dialog = QtWidgets.QDialog(self)
        self.dialog.setStyleSheet('background-color: white')

        fbox = QtWidgets.QFormLayout(self.dialog)
        fbox.addRow(QtWidgets.QLabel("Word1"))
        fbox.addRow("POS", QtWidgets.QLineEdit())
        fbox.addRow("Lemma", QtWidgets.QLineEdit())
        fbox.addRow("Level", QtWidgets.QLineEdit())

        fbox.addWidget(QtWidgets.QLabel(""))

        self.dialog.addButton = QtWidgets.QPushButton("Add")
        fbox.addRow(QtWidgets.QLabel("Rules"))
        fbox.addRow("Pattern1", QtWidgets.QLineEdit())
        fbox.addRow("Pattern2", QtWidgets.QLineEdit())
        fbox.addRow("Pattern3", QtWidgets.QLineEdit())

        button = QtWidgets.QPushButton()
        button.setIcon(QtGui.QIcon("icons/add.png"))
        button.setFlat(True)
        button.setStyleSheet("border: none")
        fbox.addRow(button, QtWidgets.QLabel(""))

        self.dialog.setLayout(fbox)
        self.dialog.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Editor()
    window.show()

    try:
        sys.exit(app.exec_())
    except:
        print("exiting")
        sys.exit(1)
