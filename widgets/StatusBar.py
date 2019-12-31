from PyQt5 import QtCore, QtGui, QtWidgets


class StatusBar(QtWidgets.QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet('background-color: #EAEAEA')

        self.lineLabel = QtWidgets.QLabel('ཐིག་ཤར།')
        self.lineLabel.setMinimumWidth(100)
        self.addPermanentWidget(self.lineLabel, 0)

        self.modeLabel = QtWidgets.QLabel('བྱ་བ།')
        self.modeLabel.setMinimumWidth(100)
        self.addPermanentWidget(self.modeLabel, 0)

        self.viewLabel = QtWidgets.QLabel('མཆན་བྱང་།')
        self.viewLabel.setMinimumWidth(100)
        self.addPermanentWidget(self.viewLabel, 0)

        self.showMessage('ཁམས་བཟང་།')
