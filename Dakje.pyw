# django setup
import os
import logging
from horology import timed
import multiprocessing

import django
import pybo

from PyQt5.QtWidgets import QTextEdit

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
django.setup()

# editor
import sys
import pathlib
from functools import partial, wraps
from collections import Counter
from PyQt5 import QtCore, QtWidgets, QtGui
from django.db import transaction

from widgets import (MenuBar, ToolBar, StatusBar, CentralWidget,
                     EditTokenDialog, Highlighter, Tabs)
                    #  EditTokenDialog, Highlighter, DictionaryEditorWidget)

from managers import ActionManager, TokenManager, ViewManager, FormatManager, Token 
from web.settings import BASE_DIR, FILES_DIR

from storage.models import Token, Setting
# flushes the Tokens on start, should be in a function
Token.objects.all().delete()


# Highlighting profile settings
LEVEL_PROFILE_PATH = ''
# TODO record checkbox state
HIGHLIGHTING_STATE = ''


# Exception
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

def ignoreEvent(signal):
    def d(func):
        func.ignoreSignals = []

        @wraps(func)
        def f(*args, **kws):
            if signal in func.ignoreSignals:
                # print(f"{func} ignore {signal}")
                return None
            else:
                # print(f"{func} called by {signal}")
                return func(*args, **kws)
        return f
    return d

class Editor(QtWidgets.QMainWindow):
    BASE_DIR = os.path.dirname(__name__)
    SEG_TRIGGERS = ['་', '།', '\n']

    @timed(unit='ms')
    def __init__(self, parent=None):
        super().__init__(parent)

        self.undoStack = QtWidgets.QUndoStack(self)

        self.initProperties()
        self.initManagers()
        self.initUI()
        self.bindEvents()
        self.initTokenizer()
        self.setWindowTitle("དག་བྱེད།")
        self.setWindowIcon(QtGui.QIcon(
            os.path.join(BASE_DIR, "icons", "dakje.ico")))
        self.setWindowState(QtCore.Qt.WindowMaximized)
        # self.wordcount = 0

        self.textEdit.setPlainText = self.ignoreTextChanged(
            self.ignoreCursorPositionChanged(self.textEdit.setPlainText))
        self.textEdit.setSelection = self.ignoreTextChanged(
            self.ignoreCursorPositionChanged(self.textEdit.setSelection))
        self.initLevelProfile()

    # why?
    def _ignoreEvent(self, func, signal, event):
        def _func(*arg, **kwargs):
            event.__func__.ignoreSignals.append(signal)
            func(*arg, **kwargs)
            event.__func__.ignoreSignals.remove(signal)
        return _func

    def ignoreCursorPositionChanged(self, func):
        return self._ignoreEvent(func,
                                 QTextEdit.cursorPositionChanged,
                                 self.cursorPositionChanged)

    def ignoreTextChanged(self, func):
        return self._ignoreEvent(func,
                                 QTextEdit.textChanged,
                                 self.textChanged)

    def initTokenizer(self):
        self.tokenizer = pybo.WordTokenizer(
            'POS',
            tok_modifs= self.tokenManager.TRIE_MODIF_DIR
        )

    def initProperties(self):
        self.tokens = []
        self.formats = []
        self.mode = 'གསལ་ཆ།'  # LEVEL_MODE, EDITOR_MODE
        self.view = None  # PLAIN_TEXT_VIEW, SPACE_VIEW...
        self.filename = None

        self.editTokenDialog = EditTokenDialog(self)
        # self.dictionaryDialog = DictionaryEditorWidget(self)

    def initManagers(self):
        self.actionManager = ActionManager(self)
        self.tokenManager = TokenManager(self)
        self.tokenList = Token(self)
        self.viewManager = ViewManager(self)
        self.formatManager = FormatManager(self)

    def initUI(self):

        # UI font and font size
        self.uiFont = QtGui.QFont()
        self.uiFont.setFamily("Microsoft Himalaya")
        self.uiFont.setPointSize(12)

        self.actionManager.createActions()

        self.menuBar = MenuBar(self.actionManager, parent=self)
        self.menuBar.setFont(self.uiFont)
        self.setMenuBar(self.menuBar)

        # TODO group doesn't really work for mutually exclusive, has to be done manually
        # self.viewActionGroup =  QtWidgets.QActionGroup(self)
        # self.viewActionGroup.addAction(self.actionManager.spaceViewAction)
        # self.viewActionGroup.addAction(self.actionManager.tagViewAction)

        self.toolBar = ToolBar(self.actionManager, parent=self)
        self.addToolBar(self.toolBar)

        self.statusBar = StatusBar(parent=self)
        self.statusBar.modeLabel.setFont(self.uiFont)
        self.statusBar.viewLabel.setFont(self.uiFont)
        self.statusBar.lineLabel.setFont(self.uiFont)
        self.setStatusBar(self.statusBar)

        self.centralWidget = CentralWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.highlighter = Highlighter(self.textEdit.document(), self)

        # textEdit font and font size
        self.font = QtGui.QFont()
        self.font.setFamily("Microsoft Himalaya")
        self.font.setPointSize(12)

        self.setStyleSheet('QMainWindow{background-color: white}')
        self.textEdit.setStyleSheet(
            'border: none; margin: 10px')
        self.textEdit.setFont(self.font)

        # font family
        self.toolBar.addSeparator()
        self.fontPicker = QtWidgets.QFontComboBox()
        self.toolBar.addWidget(self.fontPicker)
        self.fontPicker.setCurrentFont(self.textEdit.currentFont())

        # font size
        FONT_SIZES = [6, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]
        self.fontResizer = QtWidgets.QComboBox()
        self.toolBar.addWidget(self.fontResizer)
        self.fontResizer.addItems([str(s) for s in FONT_SIZES])
        self.fontResizer.setCurrentText(str(self.font.pointSize()))

        # update when font or size is changed
        self.fontPicker.currentFontChanged.connect(self.changeFont)
        self.fontResizer.currentIndexChanged.connect(self.changeFont)

    def changeFont(self):
        self.font = self.fontPicker.currentFont()
        self.font.setPointSize(int(self.fontResizer.currentText()))
        self.textEdit.setFont(self.font)


    def bindEvents(self):
        self.bindCursorPositionChanged()
        self.bindTextChanged()
        self.bindProfileButton()
        self.bindProfileCheckbox()
        self.bindLevelButtons()
        self.bindReloadProfileButton()

    def bindCursorPositionChanged(self):
        self.textEdit.cursorPositionChanged.connect(self.cursorPositionChanged)

    def bindTextChanged(self):
        self.textEdit.textChanged.connect(self.textChanged)

    def bindProfileButton(self):
        self.levelTab.levelProfileButton.clicked.connect(
            partial(self.loadLevelProfile))

    def bindProfileCheckbox(self):
        self.levelTab.levelProfileCheckbox.stateChanged.connect(
            partial(self.changeLevelCheckboxes))

    def bindReloadProfileButton(self):
        self.levelTab.levelReloadButton.clicked.connect(
            partial(self.reloadLevelProfile))

    def bindLevelButtons(self):
        # turn this into a loop for more levels
        self.levelTab.level1Button.clicked.connect(
            partial(self.importLevelList, level=1, levelButton=self.levelTab.level1Button))

        self.levelTab.level2Button.clicked.connect(
            partial(self.importLevelList, level=2, levelButton=self.levelTab.level2Button))

        self.levelTab.level3Button.clicked.connect(
            partial(self.importLevelList, level=3, levelButton=self.levelTab.level3Button))

        self.levelTab.level4Button.clicked.connect(
            partial(self.importLevelList, level=4, levelButton=self.levelTab.level4Button))

    def changeLevelCheckboxes(self):
        if self.levelTab.levelProfileCheckbox.isChecked():
            self.levelTab.level1Checkbox.setChecked(True)
            self.levelTab.level2Checkbox.setChecked(True)
            self.levelTab.level3Checkbox.setChecked(True)
            self.levelTab.level4Checkbox.setChecked(True)
        else:
            self.levelTab.level1Checkbox.setChecked(False)
            self.levelTab.level2Checkbox.setChecked(False)
            self.levelTab.level3Checkbox.setChecked(False)
            self.levelTab.level4Checkbox.setChecked(False)
        self.refreshView()

    def closeEvent(self, *args, **kwargs):

        import pickle
        with self.bt.pickled_file.open('wb') as f:
            pickle.dump(self.bt.head, f, pickle.HIGHEST_PROTOCOL)

        super().closeEvent(*args, **kwargs)

    def copy(self):
        self.textEdit.copy()

    def paste(self):
        self.textEdit.paste()

    def cut(self):
        self.textEdit.cut()

    def toggleSpaceView(self):
        if self.viewManager.isPlainTextView():
            self.segment()
        
        self.viewManager.toggleSpaceView()
        self.refreshView()

    def toggleTagView(self):
        if self.viewManager.isPlainTextView():
            self.segment()
        self.viewManager.toggleTagView()
        self.refreshView()

    @timed(unit='ms', name='editor.segment: ')
    def segment(self, byShunit=True, breakLine=False):
        """
        1. Gets the text in textedit, 2. segments it with pybo,
        3. assigns a lists of Token objects to self.tokens,
        4. displays text with refreshview().

        """
        print('editor.segment: start')

        if byShunit:
            # find shunit in 

            block = self.textEdit.textCursor().block()
            string = block.text()
            # print(string)

            if breakLine:
                block = block.previous()
                string = block.text() + '\n'

            tokens = self.tokenManager.segment(string)
            startIndex, endIndex = self.tokenManager.findByBlockIndex(
                block.blockNumber())

            if startIndex is None:
                self.tokens.extend(tokens)

            else:
                self.tokens[startIndex: endIndex + 1] = tokens

            string = self.centralWidget.textEdit.toPlainText()
            self.tokens = self.tokenManager.segment(string)

        else:
            string = self.centralWidget.textEdit.toPlainText()
            self.tokens = self.tokenManager.segment(string)

        self.refreshView()
        print('editor.segment: end')

    def resegment(self):
        # used after updateToken()
        # updateToken() not used
        string = ''.join([token.text for token in self.tokens])
        tokens = self.tokenManager.segment(string)
        self.tokens = tokens
        self.refreshView()

    @property
    def bt(self):
        return self.tokenizer.tok.trie

    # TextEdit #
    @property
    def textEdit(self):
        return self.centralWidget.textEdit

    @property
    def findWidget(self):
        return self.centralWidget.leftTabWidget.findTab

    @property
    def levelTab(self):
        return self.centralWidget.tabWidget.levelTab

    @property
    def editorTab(self):
        return self.centralWidget.tabWidget.editorTab

    def isLevelMode(self):
        return (self.centralWidget.tabWidget.currentIndex() == 0)

    def isEditorMode(self):
        return (self.centralWidget.tabWidget.currentIndex() == 1)

    # TextEdit Actions #
    def newFile(self):
        self.textEdit.newFile()

    def openFile(self):
        self.textEdit.openFile()
        self.segment()

    def saveFile(self):
        self.filename = self.textEdit.saveFile()

    def undo(self):
        self.textEdit.undo()

    def redo(self):
        self.textEdit.redo()

    # TextEdit Events #
    @ignoreEvent(QTextEdit.cursorPositionChanged)
    def cursorPositionChanged(self):
        cursor = self.textEdit.textCursor()
        position = cursor.position()

        if (self.viewManager.isTagView() and
                not self.editTokenDialog.isVisible()):
            token = self.tokenManager.find(position)[1]

            if 0 > 1:
                pass
            # if token.pos == "OOV":
                # TODO deal with OOVs
                # self.actionManager.dictionaryAction.trigger()
                # self.dictionaryDialog.addWord(text=token.text)
            else:
                self.editTokenDialog.setMode(EditTokenDialog.MODE_UPDATE)
                self.editTokenDialog.setToken(token)
                self.editTokenDialog.show()

        self.showStatus(ln=cursor.blockNumber() + 1,
                        col=cursor.columnNumber() + 1)

    @ignoreEvent(QTextEdit.textChanged)
    def textChanged(self):
        if self.viewManager.isPlainTextView():
            string = self.textEdit.toPlainText()

            if any([string.endswith(w) for w in self.SEG_TRIGGERS]):
                self.segment()
                print('option1')
                # self.segment(byBlock=True)

            elif string.endswith('\n'):
                self.segment()
                print('option2')
                # TODO: block mode: bug - if we delete text and try to rewrite new
                # text it copies the already saved text.
                # self.segment(byBlock=True, breakLine=True)

            elif string == '': 
                self.segment()
                print('option3')

    def initLevelProfile(self):
        # load last level profile
        Setting.objects.update_or_create(key='profile_path')
        if Setting.objects.get(key='profile_path').value:
            self.LEVEL_PROFILE_PATH = Setting.objects.get(key='profile_path').value
            self.setLevelProfile()

    # Import Level Profile #
    def loadLevelProfile(self):
        # a profile is a dir containing level lists
        dirPath = QtWidgets.QFileDialog.getExistingDirectory(parent=self, directory=os.path.join(FILES_DIR, 'levels'), options=QtWidgets.QFileDialog.ShowDirsOnly)

        setting = Setting.objects.get(key='profile_path')
        self.LEVEL_PROFILE_PATH = setting.value = dirPath
        setting.save()
        
        self.levelTab.levelProfileLabel.setText(pathlib.Path(self.LEVEL_PROFILE_PATH).stem)
        # dirpath string
        self.setLevelProfile()

    def setLevelProfile(self):
        # clear db
        Token.objects.all().delete()

        # reset level names
        self.levelTab.level1Button.setText(Tabs.LEVEL_NAMES[0])
        self.levelTab.level2Button.setText(Tabs.LEVEL_NAMES[1])
        self.levelTab.level3Button.setText(Tabs.LEVEL_NAMES[2])
        self.levelTab.level4Button.setText(Tabs.LEVEL_NAMES[3])

        # get file paths
        if self.LEVEL_PROFILE_PATH:
            levelFiles = list(pathlib.Path(self.LEVEL_PROFILE_PATH).glob("*.txt"))
        else:
            return

        # FIXME set level lists
        if not levelFiles:
            print('Where is my file?')
            return
        if len(levelFiles) >= 1:
            self.setLevelList(level=1, levelButton=self.levelTab.level1Button, filePath=levelFiles[0])
        if len(levelFiles) >= 2:
            self.setLevelList(level=2, levelButton=self.levelTab.level2Button, filePath=levelFiles[1])
        if len(levelFiles) >= 3:
            self.setLevelList(level=3, levelButton=self.levelTab.level3Button, filePath=levelFiles[2])
        if len(levelFiles) >= 4:
            self.setLevelList(level=4, levelButton=self.levelTab.level4Button, filePath=levelFiles[3])
        if len(levelFiles) > 4:
            return


    def reloadLevelProfile(self):
        self.setLevelProfile()
        self.refreshView()

    # Import Level List
    def importLevelList(self, level, levelButton):
        # get file path
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select a level list", os.path.join(FILES_DIR, 'levels'), filter="UTF-8 ཡིག་རྐྱང་། (*.txt)")

        if not filePath:
            return
        else:
            self.setLevelList(level, levelButton, filePath)

    # @timed(unit='ms')
    def setLevelList(self, level, levelButton, filePath):

        splitFilePath = pathlib.PurePath(filePath).parts

        # get and set file name
        if '' in splitFilePath[:1]:
            return
        else:
            fileName = splitFilePath[len(splitFilePath) - 1]
            levelButton.setText(fileName)

        # get strings
        with open(filePath, encoding='utf-8') as f:
            words = [word[:-1] if word.endswith('་') else word
                     for word in [line.rstrip('\r\n')
                                  for line in f.readlines()]]

        # create words, add to level
        with transaction.atomic():
            for word in words:
                token = Token.objects.get_or_create(
                    text=word, type=Token.TYPE_UPDATE)[0]
                token.level = level
                token.save()

        self.refreshView()

    def importRuleList(self, level):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select a rule list", os.path.join(FILES_DIR, 'levels'), filter="UTF-8 ཡིག་རྐྱང་། (*.txt)")

        with open(filePath, encoding='utf-8') as f:
            rules = [line.rstrip('\r\n') for line in f.readlines()]

        self.matcher.match(self.tokens, rules)

        self.refreshView()

    def findShunit(self):
        # shunit is the text block between two shad



        pass


    # Refresh #
    # @timed(unit='ms')    # TypeError: refreshView() takes 1 positional argument but 2 were given
    def refreshView(self):

        """
        Refreshes the view without segmenting 
            :param self: 
        """
        # Adds token info from the db
        # - level
        # - sense
        self.tokenManager.applyDict()

        # adjustment rules ... defer to pybo?
        self.tokenManager.matchRules()

        # keep cursor
        textCursor = self.textEdit.textCursor()
        current = self.tokenManager.find(textCursor.position())
        # print(f'current: {current[0]}')

        if current is not None:
            currentToken = current[1]
            distance = textCursor.position() - currentToken.start
            print(f'current: {current[0]}, {current[1].text}')

        # Sets plain text in textEdit before moving on to highlighting
        text = self.tokenManager.getString()
        self.textEdit.setPlainText(text)

        if current is not None:
            textCursor.setPosition(currentToken.start + distance)
        else:
            textCursor.setPosition(len(self.textEdit.toPlainText()))

        self.ignoreCursorPositionChanged(
            self.textEdit.setTextCursor)(textCursor)
        self.refreshCoverage()

        # print([t.text for t in self.tokens])
        # TODO current shunit
        self.statusBar.showMessage(
            '  ' + ' '.join([t.text for t in self.tokens[-19:]]))

    @timed(unit='ms')
    def statistics(self):

        # to do: bug fix -
        # if we press enter twice sentence count reinitializes
        # you need to press on enter for it to recognize that the text editor is empty
        # it considers བོད and བོད་ different - the difference is the tseg (not sure if that is a bug)
        # It always counts the first enter

        # Statistics - analyze the text in the text editor

        wordCount = 0  # number of words written
        sentenceCount = 0  # number of sentence written - each new line is considered one sentnece
        typeCount = 0  # number of words used
        max = 0  # maximum number of words in a sentence - longest sentence
        counts = dict()
        sentenceWordCount = []  # records the number of words in each sentence
        wordSentence = 0  # words in a sentence
        verbsPerSen = 0  # verbs in a sentence
        verbSentence = []  # records the number of verbs in each sentence

        # parse through the list and not count the newline
        # for now every newline is considered a completion of one sentence
        for token in self.tokens:

            if token.text == "།":
                continue
            if token.text != "\n":
                wordCount += 1
                wordSentence += 1
                if token.pos == "VERB":
                    verbsPerSen += 1
                if token.text in counts:
                    continue
                else:
                    counts[token.text] = 1
                    typeCount += 1
            else:
                if wordCount == 0:
                    continue
                verbSentence.append(verbsPerSen)
                sentenceCount += 1
                sentenceWordCount.append(wordSentence)
                if max < sentenceWordCount[sentenceCount - 1]:
                    max = sentenceWordCount[sentenceCount - 1]
                wordSentence = 0
                verbsPerSen = 0

        # print("maximum words in a sentence: ", max)
        # print("word count: ", wordCount)
        # print("type count: ", typeCount)
        # print("sentence count: ", sentenceCount)

        # frequency - the number of times a token is repeated
        frequency = Counter([
            (token.text, token.type, token.pos, token.text_unaffixed) for token in self.tokens])
        # print("Frequency: ", frequency)

        # Updating the Statistics
        self.levelTab.wordCountLabel.setText(str(wordCount))
        self.levelTab.typeCountLabel.setText(str(typeCount))
        self.levelTab.senCountLabel.setText(str(sentenceCount))
        self.levelTab.maxWordLabel.setText(str(max))
    
    @timed(unit='ms')
    def refreshCoverage(self):

        tokenNum = sum(1 for t in self.tokens if t.type == 'TEXT')
        # print('tokenNum: ', tokenNum)

        self.statistics()

        levelCounter = Counter([
            token.level for token in self.tokens if token.type == 'TEXT'])


        def getLevelPercentage(key):
            if tokenNum == 0:
                return 0
            else:
                print(f'{key}: {levelCounter[key] / tokenNum * 100.0}')
                return levelCounter[key] / tokenNum * 100.0

        # update 
        if self.tokens:
            self.levelTab.tokenCoverageProgBar.setValue(100 - getLevelPercentage(None))

        self.levelTab.levelNoneProgBar.setValue(getLevelPercentage(None))
        self.levelTab.level1ProgBar.setValue(getLevelPercentage(1))
        self.levelTab.level2ProgBar.setValue(getLevelPercentage(2))
        self.levelTab.level3ProgBar.setValue(getLevelPercentage(3))
        self.levelTab.level4ProgBar.setValue(getLevelPercentage(4))

        posCounter = Counter([
            token.pos for token in self.tokens])

        posFreq = posCounter.most_common()
        # print(posFreq)
        """
        if len(posFreq) >= 1:
            self.editorTab.firstFreqLabel.setText(posFreq[0][0])
            self.editorTab.firstFreqProgBar.setValue(
                posFreq[0][1] / tokenNum * 100.0)

        if len(posFreq) >= 2:
            self.editorTab.secondFreqLabel.setText(posFreq[1][0])
            self.editorTab.secondFreqProgBar.setValue(
                posFreq[1][1] / tokenNum * 100.0)

        if len(posFreq) >= 3:
            self.editorTab.thirdFreqLabel.setText(posFreq[2][0])
            self.editorTab.thirdFreqProgBar.setValue(
                posFreq[2][1] / tokenNum * 100.0)
        """

    def getHighlightedLevels(self):
        result = []
        if self.levelTab.levelNoneCheckbox.isChecked():
            result.append(None)
        if self.levelTab.level1Checkbox.isChecked():
            result.append(1)
        if self.levelTab.level2Checkbox.isChecked():
            result.append(2)
        if self.levelTab.level3Checkbox.isChecked():
            result.append(3)
        if self.levelTab.level4Checkbox.isChecked():
            result.append(4)
        return result

    def getHighlightedPoses(self):
        result = []
        if self.editorTab.firstFreqCheckbox.isChecked():
            result.append(self.editorTab.firstFreqLabel.text())
        if self.editorTab.secondFreqCheckbox.isChecked():
            result.append(self.editorTab.secondFreqLabel.text())
        if self.editorTab.thirdFreqCheckbox.isChecked():
            result.append(self.editorTab.thirdFreqLabel.text())
        return result

    def getPosRank(self, pos):
        if self.editorTab.firstFreqLabel.text() == pos:
            return 1
        elif self.editorTab.secondFreqLabel.text() == pos:
            return 2
        elif self.editorTab.thirdFreqLabel.text() == pos:
            return 3
        elif self.editorTab.thirdFreqLabel.text() == pos:
            return 4
        else:
            return None

    def showStatus(self, ln=None, col=None):
        self.statusBar.modeLabel.setText(self.mode)
        self.statusBar.viewLabel.setText(self.viewManager.getStatusDisplay())

        if ln and col:
            self.statusBar.lineLabel.setText(
                f'ཐིག་ཤར། {ln} ཡིག་འབྲུ། {col} ')

def runserver():
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
    django.setup()

    from django.core.management import call_command
    call_command('runserver', '--noreload')


def main():
    multiprocessing.Process(target=runserver, daemon=True).start()

    app = QtWidgets.QApplication(sys.argv)
    window = Editor()
    window.show()

    try:
        sys.exit(app.exec_())
    except:
        print("exiting")
        sys.exit(1)


if __name__ == '__main__':
    main()
