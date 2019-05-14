from PyQt5 import QtCore, QtGui, QtWidgets


class ToolBar(QtWidgets.QToolBar):
    def __init__(self, actionManager, parent=None):
        super().__init__(parent)
        self.actionManager = actionManager
        self.setMovable(False)

        for actions in actionManager.getToolBarActions():
            self.addSeparator()
            for action in actions:
                self.addAction(action)
