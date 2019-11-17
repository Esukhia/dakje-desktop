from PyQt5 import QtCore, QtGui, QtWidgets

class MenuBar(QtWidgets.QMenuBar):
    def __init__(self, actionManager, parent=None):
        super().__init__(parent)
        self.actionManager = actionManager

        self.menuFile = QtWidgets.QMenu('&ཡིག་ཆ།')
        self.menuEdit = QtWidgets.QMenu('&Edit')
        self.menuView = QtWidgets.QMenu('&View')
        self.menuHelp = QtWidgets.QMenu('&Help')

        self.addMenu(self.menuFile)
        for action in actionManager.getMenuBarActions(actionManager.MENU_FILE):
            self.menuFile.addAction(action)

        self.addMenu(self.menuEdit)
        for action in actionManager.getMenuBarActions(actionManager.MENU_EDIT):
            self.menuEdit.addAction(action)


        self.addMenu(self.menuView)
        for action in actionManager.getMenuBarActions(actionManager.MENU_VIEW):
            self.menuView.addAction(action)

        self.addMenu(self.menuHelp)
        for action in actionManager.getMenuBarActions(actionManager.MENU_HELP):
            self.menuHelp.addAction(action)
        self.menuHelp.addAction(
            "About &Qt", QtWidgets.QApplication.instance().aboutQt)
