import os

import pybo

from PyQt5 import QtCore, QtGui, QtWidgets

from .CQLWidget import CqlQueryGenerator

from web.settings import BASE_DIR

LEVEL_MODE_EXAMPLE_STRING = '''
Statistics

...
...
...
'''

EDITOR_MODE_EXAMPLE_STRING = '''
Statistics
0 words
0 sentences
0 words per sentences
'''


class ProgressBar(QtWidgets.QProgressBar):
    def __init__(self, parent=None, value=None, color=None):
        
        super().__init__(parent)

        self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVertical_Mask)
        if value is not None:
            self.setValue(value)

        if color is not None:
            self.setStyleSheet(
                'QProgressBar::chunk {background-color: ' + color + '}')


class LevelTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initGrids()
        self.initForms()
        self.initTextBrowser()

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.vbox.addLayout(self.grids)
        self.vbox.addSpacing(50)
        self.vbox.addLayout(self.forms)
        self.vbox.addWidget(self.textBrowser)

    @property
    def editor(self):
        return self.parent().parent().parent()

    def initGrids(self):
        self.grids = QtWidgets.QGridLayout()


        # Selection Coverage
        self.tokenCoverageLabel = QtWidgets.QLabel('Selection Coverage')
        self.tokenCoverageProgBar = ProgressBar(self, 0, '#278da9')
        self.grids.addWidget(self.tokenCoverageLabel, 0, 0, 1, 4)
        self.grids.addWidget(self.tokenCoverageProgBar, 1, 0, 1, 4)

        # Grade Profile
        self.levelProfileCheckbox = QtWidgets.QCheckBox()
        self.levelProfileButton = QtWidgets.QPushButton()
        self.levelProfileButton.setFlat(True)
        self.levelProfileButton.setStyleSheet("Text-align:left")
        self.levelProfileButton.setText('Load grade profile')
        # self.grids.addWidget(self.levelProfileCheckbox, 2, 0, 1, 1)
        # self.grids.addWidget(self.levelProfileButton, 2, 1, 1, 1)

        self.levelNoneButton = QtWidgets.QPushButton()
        self.levelNoneButton.setFlat(True)
        self.levelNoneButton.setStyleSheet("Text-align:left")
        self.levelNoneButton.setText('Non-level')
        self.levelNoneProgBar = ProgressBar(
            self, 0, self.editor.formatManager.LEVEL_FORMAT_COLORS[None])

        self.level1Button = QtWidgets.QPushButton()
        self.level1Button.setFlat(True)
        self.level1Button.setStyleSheet("Text-align:left")
        self.level1Button.setText('ཚིག་ཐོ་དང་པོ།', )
        self.level1ProgBar = ProgressBar(
            self, 0, self.editor.formatManager.LEVEL_FORMAT_COLORS[1])

        self.level2Button = QtWidgets.QPushButton()
        self.level2Button.setFlat(True)
        self.level2Button.setStyleSheet("Text-align:left")
        self.level2Button.setText('ཚིག་ཐོ་གཉིས་པ།')
        self.level2ProgBar = ProgressBar(
            self, 0, self.editor.formatManager.LEVEL_FORMAT_COLORS[2])

        self.level3Button = QtWidgets.QPushButton()
        self.level3Button.setFlat(True)
        self.level3Button.setStyleSheet("Text-align:left")
        self.level3Button.setText('ཚིག་ཐོ་གསུམ་པ།')
        self.level3ProgBar = ProgressBar(
            self, 0, self.editor.formatManager.LEVEL_FORMAT_COLORS[3])

        # Checkboxes
        self.levelNoneCheckbox = QtWidgets.QCheckBox()
        self.level1Checkbox = QtWidgets.QCheckBox()
        self.level2Checkbox = QtWidgets.QCheckBox()
        self.level3Checkbox = QtWidgets.QCheckBox()

        for checkbox in (self.levelProfileCheckbox, self.levelNoneCheckbox, self.level1Checkbox,
                         self.level2Checkbox, self.level3Checkbox):
            checkbox.clicked.connect(self.editor.refreshView)

        self.levelCoverages = [
            # [self.levelProfileCheckbox, self.levelProfileButton],
            [self.levelNoneCheckbox, self.levelNoneButton, self.levelNoneProgBar],
            [self.level1Checkbox, self.level1Button, self.level1ProgBar],
            [self.level2Checkbox, self.level2Button, self.level2ProgBar],
            [self.level3Checkbox, self.level3Button, self.level3ProgBar],
        ]

        for i, levelCoverage in enumerate(self.levelCoverages):
            self.levelRow = 4 + i
            self.grids.addWidget(levelCoverage[0], self.levelRow, 0, 1, 1)
            self.grids.addWidget(levelCoverage[1], self.levelRow, 1, 1, 1)
            self.grids.addWidget(levelCoverage[2], self.levelRow, 2, 1, 2)

        # Add new level
        # self.levelCoverageLabel = QtWidgets.QLabel('Level Coverage')
        # self.grids.addWidget(self.levelCoverageLabel, 2, 0, 1, 2)

        self.addBtn = QtWidgets.QPushButton('+')
        self.grids.addWidget(self.addBtn, self.levelRow+1,2,1,2)
        """
        self.addBtn.clicked.connect(self.addLevel)

        self.addLevel()

    def addLevel(self):

        add a + button in the grid
        """


    def initForms(self):
        self.forms = QtWidgets.QFormLayout()
        self.statisticsLabel = QtWidgets.QLabel('Statistics:')

        #bold statistics 
        self.statisticsLabel.setFont(QtGui.QFont("Times",10,weight=QtGui.QFont.Bold))

        # self.forms.addRow(self.statisticsLabel)
        self.editor.refreshCoverage
        
        # self.freqLabel = QtWidgets.QLabel('0')
        self.wordCountLabel = QtWidgets.QLabel('0')
        self.senCountLabel = QtWidgets.QLabel('0')
        self.typeCountLabel = QtWidgets.QLabel('0')
        self.maxWordLabel = QtWidgets.QLabel('0')

        # Word Count
        self.forms.addRow("ཐ་སྙད་སྤྱིའི་གྲངས། ",
                          self.wordCountLabel)
        self.forms.addRow("ཚིག་རིགས་ཀྱི་གྲངས། ",
                          self.typeCountLabel)
        self.forms.addRow("ཚིག་གྲུབ་གྲངས། ",
                          self.senCountLabel)
        self.forms.addRow("Max words in a Sentence count: ",
                          self.maxWordLabel)

        # self.forms.addRow("frequency: ", self.freqLabel)

    def initTextBrowser(self):
        self.textBrowser = QtWidgets.QTextBrowser()
        self.textBrowser.setText(LEVEL_MODE_EXAMPLE_STRING)


class EditorTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initErrorGrids()
        self.initErrorList()
        self.initCoverageGrids()
        self.initTextBrowser()

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.vbox.addLayout(self.errorGrids)
        self.vbox.addWidget(self.errorList)
        self.vbox.addSpacing(50)
        self.vbox.addLayout(self.coverageGrids)
        self.vbox.addWidget(self.textBrowser)

    @property
    def editor(self):
        return self.parent().parent().parent()

    def initErrorGrids(self):
        self.errorGrids = QtWidgets.QGridLayout()

        self.errorTypes = [
            [QtWidgets.QLabel('Concision'), 3, 'darkred'],
            [QtWidgets.QLabel('Clarity'), 5, 'darkblue'],
            [QtWidgets.QLabel('Logic'), 3, 'darkgreen']
        ]
        for i, errorType in enumerate(self.errorTypes):
            self.errorGrids.addWidget(errorType[0], 0, i)
            self.errorGrids.addWidget(
                QtWidgets.QPushButton(
                    styleSheet='font-weight: 900; font-size: 20px;'
                               'border: 5px solid ' + errorType[2],
                    text=str(errorType[1]),
                    minimumHeight=50
                ), 1, i)

    def initErrorList(self):
        self.errorList = QtWidgets.QListWidget(self)
        self.errorList.addItem('Error1')
        self.errorList.addItem('Error2')
        self.errorList.addItem('Error3')
        self.errorList.addItem('Error4')

    def initCoverageGrids(self):
        self.firstFreqCheckbox = QtWidgets.QCheckBox()
        self.firstFreqLabel = QtWidgets.QLabel()
        self.firstFreqProgBar = ProgressBar(self, 0, '#363d5c')
        self.secondFreqCheckbox = QtWidgets.QCheckBox()
        self.secondFreqLabel = QtWidgets.QLabel()
        self.secondFreqProgBar = ProgressBar(self, 0, '#87a840')
        self.thirdFreqCheckbox = QtWidgets.QCheckBox()
        self.thirdFreqLabel = QtWidgets.QLabel()
        self.thirdFreqProgBar = ProgressBar(self, 0, '#ddc328')

        for checkbox in (self.firstFreqCheckbox, self.secondFreqCheckbox,
                         self.thirdFreqCheckbox):
            checkbox.clicked.connect(self.editor.refreshView)

        self.coverageGrids = QtWidgets.QGridLayout()
        self.coverageLabel = QtWidgets.QLabel('Coverages')
        self.coverages = [
            [self.firstFreqCheckbox, self.firstFreqLabel, self.firstFreqProgBar],
            [self.secondFreqCheckbox, self.secondFreqLabel, self.secondFreqProgBar],
            [self.thirdFreqCheckbox, self.thirdFreqLabel, self.thirdFreqProgBar]
        ]
        self.coverageGrids.addWidget(self.coverageLabel, 0, 0, 1, 4)
        for i, coverage in enumerate(self.coverages):
            row = i + 1
            self.coverageGrids.addWidget(coverage[0], row, 0, 1, 1)
            self.coverageGrids.addWidget(coverage[1], row, 1, 1, 1)
            self.coverageGrids.addWidget(coverage[2], row, 2, 1, 2)

    def initTextBrowser(self):
        self.textBrowser = QtWidgets.QTextBrowser()
        self.textBrowser.setText(EDITOR_MODE_EXAMPLE_STRING)


class FindTab(QtWidgets.QWidget):
    MODE_SIMPLE = 1
    MODE_CQL = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initForms()
        self.initResult()
        self.hide()

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.vbox.addLayout(self.forms)
        self.vbox.addSpacing(50)
        self.vbox.addWidget(self.resultLabel)
        self.vbox.addWidget(self.resultList)

    @property
    def editor(self):
        return self.parent().parent().parent().parent()

    @property
    def textEdit(self):
        return self.editor.textEdit


    def initForms(self):
        self.forms = QtWidgets.QFormLayout()

        # Find Form
        self.findInput = QtWidgets.QLineEdit()
        self.findBtn = QtWidgets.QPushButton('Find')

        self.cqlQueryGenerator = CqlQueryGenerator(self.findInput)
        self.cqlQueryGeneratorBtn = QtWidgets.QPushButton()
        self.cqlQueryGeneratorBtn.setFlat(True)
        self.cqlQueryGeneratorBtn.setIcon(QtGui.QIcon(os.path.join(
            BASE_DIR, 'icons', 'CQL.png')))
        self.cqlQueryGeneratorBtn.setIconSize(QtCore.QSize(16, 16))
        self.cqlQueryGeneratorBtn.clicked.connect(
            lambda: self.cqlQueryGenerator.show())
        self.cqlQueryGeneratorBtn.setVisible(False)

        self.findhbox = QtWidgets.QHBoxLayout()
        self.findhbox.addWidget(self.findInput)
        self.findhbox.addWidget(self.cqlQueryGeneratorBtn)
        self.findhbox.addWidget(self.findBtn)
        self.forms.addRow(self.findhbox)

        # Find Mode Choices
        self.mode = self.MODE_SIMPLE
        self.simpleRadio = QtWidgets.QRadioButton('Simple')
        self.simpleRadio.setChecked(True)
        self.cqlRadio = QtWidgets.QRadioButton('CQL')

        self.modeChoiceshbox = QtWidgets.QHBoxLayout()
        self.modeChoiceshbox.addWidget(self.simpleRadio)
        self.modeChoiceshbox.addWidget(self.cqlRadio)
        self.forms.addRow(self.modeChoiceshbox)

        # Replace Form
        self.replaceInput = QtWidgets.QLineEdit()
        self.replaceBtn = QtWidgets.QPushButton('Replace')
        self.replaceAllBtn = QtWidgets.QPushButton('ReplaceAll')
        self.forms.addRow(self.replaceInput, self.replaceBtn)
        self.forms.addRow(None, self.replaceAllBtn)

        # Connected
        self.findBtn.clicked.connect(self._find)
        self.replaceBtn.clicked.connect(self.replace)
        self.replaceAllBtn.clicked.connect(self.replaceAll)
        self.simpleRadio.clicked.connect(self.radioChanged)
        self.cqlRadio.clicked.connect(self.radioChanged)

    def initResult(self):
        # Results
        self.resultLabel = QtWidgets.QLabel('Result')
        self.resultList = QtWidgets.QListWidget(self)

        self.resultList.itemClicked.connect(self.itemClicked)

    def radioChanged(self):
        if self.cqlRadio.isChecked():
            self.cqlQueryGeneratorBtn.setVisible(True)
            self.findInput.repaint()
        else:
            self.cqlQueryGeneratorBtn.setVisible(False)

    def _find(self):
        self.resultList.sr()

        if self.simpleRadio.isChecked():
            self.mode = self.MODE_SIMPLE
            self.findText()
        else:  # cqlRadio
            self.mode = self.MODE_CQL
            self.findCqlTokens()

        # click first
        self.clickItem(0)

    def findCqlTokens(self):
        query = self.findInput.text()
        matcher = pybo.CQLMatcher(query)
        tokens = self.editor.tokens

        slices = matcher.match([t.pyboToken for t in tokens])

        for slice in slices:
            item = QtWidgets.QListWidgetItem()
            item.slice = list(slice)
            item.setText(' '.join(
                [w.text for w in tokens[slice[0]:slice[1]+1]]))
            self.resultList.addItem(item)

        self.resultLabel.setText(str(len(slices)) + " Matches")

    def findText(self):
        query = self.findInput.text()
        matchNum = 0

        cursor = self.textEdit.textCursor()
        cursor.setPosition(0)
        self.textEdit.setTextCursor(cursor)

        while self.textEdit.find(query):
            cursor = self.textEdit.textCursor()
            item = QtWidgets.QListWidgetItem()
            item.slice = [cursor.selectionStart(), cursor.selectionEnd()]
            item.setText(cursor.selectedText())
            self.resultList.addItem(item)
            matchNum += 1

        self.resultLabel.setText(str(matchNum) + " Matches")

    def itemClicked(self, item):
        if self.mode == self.MODE_SIMPLE:
            self.textEdit.setSelection(item.slice[0], item.slice[1])
        else:
            self.textEdit.setTokensSelection(item.slice[0], item.slice[1])

    def clickItem(self, row):
        if row < self.resultList.count():
            self.resultList.setCurrentRow(row)
            self.itemClicked(self.resultList.item(row))

    def replace(self):
        if self.editor.viewManager.isPlainTextView():
            cursor = self.textEdit.textCursor()
            if cursor.hasSelection():
                cursor.insertText(self.replaceInput.text())
                self.editor.segment()
                self._find()
        else:
            QtWidgets.QMessageBox.warning(
                self, 'Mode Error',
                'Please replace text in plain text mode.',
                buttons=QtWidgets.QMessageBox.Ok
            )

    def replaceAll(self):
        if self.editor.viewManager.isPlainTextView():
            for _ in range(self.resultList.count()):
                self.clickItem(0)
                self.replace()
        else:
            QtWidgets.QMessageBox.warning(
                self, 'Mode Error',
                'Please replace text in plain text mode.',
                buttons=QtWidgets.QMessageBox.Ok
            )


class CorpusAnalysisTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.forms = QtWidgets.QFormLayout()
