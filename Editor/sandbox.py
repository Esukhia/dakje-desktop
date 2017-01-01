import sys
from PyQt5.QtWidgets import (QWidget, QGridLayout, QLabel, QRadioButton, QCheckBox,
                            QPushButton, QApplication)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

count = 1

class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.button = QPushButton('Add list')
        self.grid.addWidget(self.button, 0, 0)
        self.button.clicked.connect(self.Add)
        self.setWindowTitle('Add List Widget')

    def Add(self):
        global count
        self.checkBox = QCheckBox()
        self.checkBox.setObjectName('radio{}'.format(count))
        self.checkBox.setChecked(True)
        self.grid.addWidget(self.checkBox, count, 0, 1, 1)

        self.label = QLabel(str(count))
        self.label.setStyleSheet("QLabel {background-color: red;}")
        self.label.setAlignment(Qt.AlignLeft)
        self.grid.addWidget(self.label, count, 1, 1, 1)

        color = QPixmap(16, 16)
        color.fill(Qt.blue)
        self.colorLabel = QLabel()
        self.colorLabel.setPixmap(color)
        self.grid.addWidget(self.colorLabel, count, 2)

        b = QPushButton('button '+str(count), self)
        self.checkBox.clicked.connect(self.stuff)
        b.clicked.connect(self.buttonCopy)
        self.grid.addWidget(b, count, 3)

        count += 1

    def buttonCopy(self):
        sender = self.sender()
        print(sender.text())

    def stuff(self):
        sender = self.sender()
        print('clicked: '+sender.objectName())


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())


# Dynamically add buttons

# import sys
# from PyQt5.QtWidgets import (QWidget, QGridLayout,
#                             QPushButton, QApplication)
# count = 1

# class Example(QWidget):

#     def __init__(self):
#         super().__init__()

#         self.initUI()

#     def initUI(self):

#         self.grid = QGridLayout()
#         self.setLayout(self.grid)

#         self.button = QPushButton('ADD')
#         self.grid.addWidget(self.button, 0, 0)
#         self.button.clicked.connect(self.Add)
#         self.setWindowTitle('Calculator')

#     def Add(self):
#         print('hi')
#         global count
#         b = QPushButton('button '+str(count), self)
#         b.clicked.connect(self.buttonCopy)
#         self.grid.addWidget(b, count, 0)

#         count += 1

#     def buttonCopy(self):
#         print('ha')
#         sender = self.sender()
#         print(sender.text())

#         # self.move(300, 150)

# if __name__ == '__main__':

#     app = QApplication(sys.argv)
#     ex = Example()
#     ex.show()
#     sys.exit(app.exec_())


# Dynamically generate table of buttons

# import sys
# from PyQt5.QtWidgets import (QWidget, QGridLayout, 
#     QPushButton, QApplication)


# class Example(QWidget):

#     def __init__(self):
#         super().__init__()

#         self.initUI()

#     def initUI(self):

#         grid = QGridLayout()
#         self.setLayout(grid)

#         names = ['Cls', 'Bck', '', 'Close',
#                  '7', '8', '9', '/',
#                  '4', '5', '6', '*',
#                  '1', '2', '3', '-',
#                  '0', '.', '=', '+']

#         positions = [(i, j) for i in range(5) for j in range(4)]
#         print(positions)

#         for position, name in zip(positions, names):

#             if name == '':
#                 continue
#             button = QPushButton(name)
#             print(position)
#             grid.addWidget(button, *position)

#         self.move(300, 150)
#         self.setWindowTitle('Calculator')
#         self.show()

# if __name__ == '__main__':

#     app = QApplication(sys.argv)
#     ex = Example()
#     sys.exit(app.exec_())