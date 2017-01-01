#!/usr/bin/env python

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from Files import UI

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = UI.Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

