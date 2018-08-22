from PyQt5 import QtCore, QtGui, QtWidgets

from untitled import Ui_MainWindow

import sys
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    window = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()

    ui.setupUi(window)
    ui.retranslateUi(window)
    
    window.showMaximized()

    try:
        sys.exit(app.exec_())
    except:
        print("exiting")
        sys.exit(1)