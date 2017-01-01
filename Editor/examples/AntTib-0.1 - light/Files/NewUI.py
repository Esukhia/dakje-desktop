# -*- coding: utf-8 -*-

import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from TibTK import AntTib, Segment, AntPut

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(435, 225)
        Form.setWindowIcon(QIcon('icon.png'))
        Form.setWindowTitle('AntTib Converter')

        # Set Form Grid
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 5, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 5, 0, 1, 1)


        # Set source and target file labels
        self.sourceLabel = QtWidgets.QLabel(Form)
        self.sourceLabel.setObjectName("sourceLabel")
        self.sourceLabel.setText('')
        self.gridLayout.addWidget(self.sourceLabel, 1, 1, 1, 1)
        self.sourceNameLabel = QtWidgets.QLabel(Form)
        self.sourceNameLabel.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.sourceNameLabel.setText("")
        self.sourceNameLabel.setObjectName("sourceNameLabel")
        self.gridLayout.addWidget(self.sourceNameLabel, 1, 2, 1, 2)

        self.targetLabel = QtWidgets.QLabel(Form)
        self.targetLabel.setObjectName("targetLabel")
        self.gridLayout.addWidget(self.targetLabel, 2, 1, 1, 1)
        self.targetNameLabel = QtWidgets.QLabel(Form)
        self.targetNameLabel.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.targetNameLabel.setText("")
        self.targetNameLabel.setObjectName("targetNameLabel")
        self.gridLayout.addWidget(self.targetNameLabel, 2, 2, 1, 2)


        # Set message dialog
        self.dialogLabel = QtWidgets.QLabel(Form)
        self.dialogLabel.setStyleSheet("color: rgb(0, 0, 255);")
        self.dialogLabel.setLineWidth(1)
        self.dialogLabel.setMidLineWidth(-1)
        self.dialogLabel.setAlignment(QtCore.Qt.AlignBottom)
        self.dialogLabel.setObjectName("dialogLabel")
        self.gridLayout.addWidget(self.dialogLabel, 3, 0, 1, 3)

        # Set main button
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 3, 3, 1, 1)
        self.pushButton.setToolTip('བཀྲ་ཤིས་བདེ་ལེགས། \n ཁྱེད་རང་བདེ་མོ་ཨེ་ཡིན།')

        # Set button group
        self.buttons = QtWidgets.QButtonGroup()

        # Set "from Unicode" group box and radio buttons
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout.setObjectName("formLayout")

        self.cutButton = QtWidgets.QRadioButton(self.groupBox)
        self.cutButton.setObjectName("radioButton")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.cutButton)
        self.buttons.addButton(self.cutButton)

        self.joinWordsButton = QtWidgets.QRadioButton(self.groupBox)
        self.joinWordsButton.setObjectName("joinWordsButton")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.joinWordsButton)
        self.buttons.addButton(self.joinWordsButton)

        self.toAntTibButton = QtWidgets.QRadioButton(self.groupBox)
        self.toAntTibButton.setObjectName("toAntTibButton")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.toAntTibButton)
        self.buttons.addButton(self.toAntTibButton)

        self.gridLayout.addWidget(self.groupBox, 0, 1, 1, 3)

        # Set "from AntTib" group box and radio buttons
        self.groupBox_2 = QtWidgets.QGroupBox(Form)
        self.groupBox_2.setObjectName("groupBox_2")
        self.formLayout_2 = QtWidgets.QFormLayout(self.groupBox_2)
        self.formLayout_2.setObjectName("formLayout_2")

        self.plainTextButton = QtWidgets.QRadioButton(self.groupBox_2)
        self.plainTextButton.setObjectName("plainTextButton")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.plainTextButton)
        self.buttons.addButton(self.plainTextButton)

        self.clusterButton = QtWidgets.QRadioButton(self.groupBox_2)
        self.clusterButton.setObjectName("clusterButton")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.clusterButton)
        self.buttons.addButton(self.clusterButton)

        self.wordListButton = QtWidgets.QRadioButton(self.groupBox_2)
        self.wordListButton.setObjectName("wordListButton")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.wordListButton)
        self.buttons.addButton(self.wordListButton)

        self.keywordListButton = QtWidgets.QRadioButton(self.groupBox_2)
        self.keywordListButton.setObjectName("keywordListButton")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.keywordListButton)
        self.buttons.addButton(self.keywordListButton)

        self.ngramButton = QtWidgets.QRadioButton(self.groupBox_2)
        self.ngramButton.setObjectName("ngramButton")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.ngramButton)
        self.buttons.addButton(self.ngramButton)

        self.concordanceButton = QtWidgets.QRadioButton(self.groupBox_2)
        self.concordanceButton.setObjectName("concordanceButton")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.concordanceButton)
        self.buttons.addButton(self.concordanceButton)

        self.collocatesButton = QtWidgets.QRadioButton(self.groupBox_2)
        self.collocatesButton.setObjectName("collocatesButton")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.collocatesButton)
        self.buttons.addButton(self.collocatesButton)

        self.levelListButton = QtWidgets.QRadioButton(self.groupBox_2)
        self.levelListButton.setObjectName("levelListButton")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.levelListButton)
        self.buttons.addButton(self.levelListButton)

        self.levelTagsButton = QtWidgets.QRadioButton(self.groupBox_2)
        self.levelTagsButton.setObjectName("levelTagsButton")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.levelTagsButton)
        self.buttons.addButton(self.levelTagsButton)

        self.profileButton = QtWidgets.QRadioButton(self.groupBox_2)
        self.profileButton.setObjectName("profileButton")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.profileButton)
        self.buttons.addButton(self.profileButton)

        self.gridLayout.addWidget(self.groupBox_2, 0, 0, 3, 1)

# Slots and Signals
        self.retranslateUi(Form)

        self.cutButton.clicked.connect(self.openFile)
        self.joinWordsButton.clicked.connect(self.openFile)
        self.toAntTibButton.clicked.connect(self.openFile)
        self.plainTextButton.clicked.connect(self.openFile)
        self.concordanceButton.clicked.connect(self.openFile)
        self.wordListButton.clicked.connect(self.openFile)
        self.keywordListButton.clicked.connect(self.openFile)
        self.ngramButton.clicked.connect(self.openFile)
        self.clusterButton.clicked.connect(self.openFile)
        self.collocatesButton.clicked.connect(self.openFile)
        self.levelListButton.clicked.connect(self.openFile)
        self.levelTagsButton.clicked.connect(self.openFile)
        self.profileButton.clicked.connect(self.openFile)

        self.pushButton.clicked.connect(self.convert)

        QtCore.QMetaObject.connectSlotsByName(Form)


# Methods

    def convert(self, Form):
        seg = Segment()
        ant = AntTib()

        if self.cutButton.isChecked():
            self.newcontent = seg.segment(self.content, ant_segment=0, unknown=0)
            self.saveFile()
        elif self.joinWordsButton.isChecked():
            self.newcontent = ant.no_space(self.content)
            self.saveFile()
        elif self.toAntTibButton.isChecked():
            self.newcontent = ant.to_ant_text(self.content)
            self.saveFile()
        elif self.plainTextButton.isChecked():
            self.newcontent = ant.from_ant_text(self.content)
            self.saveFile()
        elif self.concordanceButton.isChecked():
            self.newcontent = ant.concordance(self.content)
            print("love")
            self.saveFile()
        elif self.wordListButton.isChecked():
            self.newcontent = ant.word_list(self.content)
            self.saveFile()
        elif self.keywordListButton.isChecked():
            self.newcontent = ant.keyword_list(self.content)
            self.saveFile()
        elif self.ngramButton.isChecked():
            self.newcontent = ant.ngram(self.content)
            self.saveFile()
        elif self.clusterButton.isChecked():
            self.newcontent = ant.cluster(self.content)
            self.saveFile()
        elif self.collocatesButton.isChecked():
            self.newcontent = ant.collocates(self.content)
            self.saveFile()
        elif self.levelListButton.isChecked():
            self.newcontent = ant.words(self.content)
            self.saveFile()
        elif self.levelTagsButton.isChecked():
            self.newcontent = ant.profiler_tags(self.content)
            self.saveFile()
        elif self.profileButton.isChecked():
            self.newcontent = ant.profiler_stats(self.content)
            self.saveFile()

    def openFile(self, Form):
        if self.cutButton.isChecked():
            self.suffix = "_cut.txt"
            self.pushButton.setText('Cut Words')
        elif self.joinWordsButton.isChecked():
            self.suffix = "_jnd.txt"
            self.pushButton.setText('Cut and Spell')
        elif self.toAntTibButton.isChecked():
            self.suffix = "_ant.txt"
        else:
            self.suffix = "_uni.txt"
            self.pushButton.setText('Convert')

        self.pathname = QtWidgets.QFileDialog.getOpenFileName(None, '', '')[0]
        self.filename = str(os.path.basename(self.pathname))
        if self.filename[-4:] == '.txt':
            with open(self.pathname, 'r', -1, 'utf-8-sig') as f:
                self.content = f.read()
            self.sourceNameLabel.setStyleSheet("background-color: rgb(255, 255, 255);")
            self.sourceNameLabel.setText(" " + self.filename)
            self.targetNameLabel.setText(" " + self.filename[:-4] + self.suffix)
            self.dialogLabel.setText('Preview: ' + self.content[:40] + ' ...')
            self.targetNameLabel.setStyleSheet("background-color: rgb(225, 225, 225); color: rgb(100, 100, 100);")
        else:
            self.dialogLabel.setText("Select a '.txt' file and try again!")
            self.sourceNameLabel.setStyleSheet("background-color: rgb(255, 255, 255); color: rgb(225, 0, 0); font: italic")
            self.sourceNameLabel.setText(" " + self.filename)

    def saveFile(self):
        try:
            with open(self.filename[:-4] + self.suffix, 'w', -1, 'utf-8-sig') as f:
                f.write(self.newcontent)
            self.dialogLabel.setText('Preview: ' + self.newcontent[:40] + ' ...')
            self.sourceNameLabel.setStyleSheet("background-color: rgb(225, 225, 225); color: rgb(100, 100, 100);")
            self.targetNameLabel.setStyleSheet("background-color: rgb(255, 255, 255); color: rgb(0, 0, 0);")
        except:
            self.dialogLabel.setText('Did you pick the right task?')



    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        self.dialogLabel.setText(_translate("Form", " Pick a convertion task."))
        self.pushButton.setText(_translate("Form", "Convert"))
        self.sourceLabel.setText(_translate("Form", "Source:"))
        self.targetLabel.setText(_translate("Form", "Target:"))
        self.groupBox.setTitle(_translate("Form", "Unicode"))
        self.cutButton.setText(_translate("Form", "Cut Words"))
        self.joinWordsButton.setText(_translate("Form", "Join Words"))
        self.toAntTibButton.setText(_translate("Form", "Unicode to AntTib"))
        self.groupBox_2.setTitle(_translate("Form", "AntTib to Unicode"))
        self.plainTextButton.setText(_translate("Form", "Text"))
        self.clusterButton.setText(_translate("Form", "Cluster"))
        self.wordListButton.setText(_translate("Form", "Word List"))
        self.keywordListButton.setText(_translate("Form", "Keyword List"))
        self.ngramButton.setText(_translate("Form", "N-gram"))
        self.concordanceButton.setText(_translate("Form", "Concordance"))
        self.collocatesButton.setText(_translate("Form", "Collocates"))
        self.levelListButton.setText(_translate("Form", "Level List"))
        self.levelTagsButton.setText(_translate("Form", "Level/Tags"))
        self.profileButton.setText(_translate("Form", "Ant Profile"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

