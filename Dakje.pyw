import time
# django setup
import os
from horology import timed
import multiprocessing

import django
import pybo
import botok
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QTextEdit, QApplication
from PyQt5.QtCore import pyqtSignal
from django.db.backends.base.features import BaseDatabaseFeatures
from turtledemo.penrose import star
from django.conf.locale import tr

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
django.setup()

# editor
import sys
import pathlib
import threading
from diff_match_patch import diff
from functools import partial, wraps
from collections import Counter
from PyQt5 import QtCore, QtWidgets, QtGui
from django.db import transaction
from django.utils import translation

from widgets import (MenuBar, ToolBar, StatusBar, CentralWidget,
                     EditTokenDialog, Highlighter, Tabs)
                    #  EditTokenDialog, Highlighter, DictionaryEditorWidget)

from managers import ActionManager, TokenManager, ViewManager, FormatManager, Token
from managers.TokenManager import TokenList
from web.settings import (
    BASE_DIR, FILES_DIR, _SEG_TRIGGERS as _SEG_TRIGGERS, TEST_BY_ENG)

if TEST_BY_ENG:
    from tests import EngTokenizer as Tokenizer
else:
    from botok import WordTokenizer as Tokenizer

from storage.models import Token, Setting
# flushes the Tokens on start, should be in a function
# Token.objects.all().delete()

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
    SEG_TRIGGERS = _SEG_TRIGGERS

    @timed(unit='ms')
    def __init__(self, parent=None):
        super().__init__(parent)

        language = Setting.objects.get(key='language')
        language = language.value
        translation.activate(language)

        self.undoStack = QtWidgets.QUndoStack(self)

        self.initProperties()
        self.initManagers()
        self.fetchLevelProfile()
        self.initUI()
        self.bindEvents()
        self.initTokenizer()
        self.setWindowTitle("དག་བྱེད། Dakje")
        self.setWindowIcon(QtGui.QIcon(
            os.path.join(BASE_DIR, "icons", "dakje.ico")))
        self.setWindowState(QtCore.Qt.WindowMaximized)
        # self.wordcount = 0

        # setPlainText -> textChanged, do not want it doing every time.
        # so, add textChange signal into itself (ignoreSignals)
        # if trigger(setPlainText.ignoreSignal == textChange), skip
        self.textEdit.setPlainText = self.ignoreCursorPositionChanged(self.textEdit.setPlainText)
        self.textEdit.setSelection = self.ignoreCursorPositionChanged(self.textEdit.setSelection)
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

#     def ignoreTextChanged(self, func):
#         return self._ignoreEvent(func,
#                                  QTextEdit.textChanged,
#                                  self.textChanged)

    def initTokenizer(self):
        # self.tokenizer = Tokenizer(
        #     'POS',
        #     tok_modifs= self.tokenManager.TRIE_MODIF_DIR
        # )
        config = botok.Config.from_path(self.tokenManager.LANG_PACK_DIR)
        self.tokenizer = Tokenizer(config=config)


    def initProperties(self):
        self.tokens = TokenList() # TokenList()
#         self.tokens = []
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
        self.font.setPointSize(14)

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

        self.statThreads = []
        self.refreshThreads = []

#         self.html2 = open('t2.html').read()

    def changeFont(self):
        self.font = self.fontPicker.currentFont()
        self.font.setPointSize(int(self.fontResizer.currentText()))
        self.textEdit.setFont(self.font)


    def bindEvents(self):
        self.bindCursorPositionChanged()
#         self.bindTextChanged()
        self.bindProfileButton()
        self.bindProfileCheckbox()
        self.bindLevelButtons()
        self.bindReloadProfileButton()

    def bindCursorPositionChanged(self):
        self.textEdit.cursorPositionChanged.connect(self.cursorPositionChanged)

#     def bindTextChanged(self):
#         self.textEdit.textChanged.connect(self.textChanged)

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
        self.segment(isHighlight=True)

    def closeEvent(self, *args, **kwargs):

        import pickle
        with self.bt.pickled_file.open('wb') as f:
            pickle.dump(self.bt.head, f, pickle.HIGHEST_PROTOCOL)

        super().closeEvent(*args, **kwargs)

    def copy(self):
        self.textEdit.copy()

    def paste(self):
        self.textEdit.paste()
        string = self.textEdit.toPlainText()
        if any(e in string for e in self.SEG_TRIGGERS):
            self.segment()
#             print('paste string, including SEG_TRIGGERS -> doing the segment')

    def cut(self):
        self.textEdit.cut()
        string = self.textEdit.toPlainText()
        if any(e in string for e in self.SEG_TRIGGERS):
            self.segment()
#             print('cut string, including SEG_TRIGGERS -> doing the segment')

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
    def segment(self, byShunit=True, breakLine=False, isHighlight=False):
        """
        1. Gets the text in textedit, 2. segments it with pybo,
        3. assigns a lists of Token objects to self.tokens,
        4. displays text with refreshview().
        """
        print('editor.segment: start')
        # python profile
        tokenStart = None
        tokenEnd = None
        afterChangingString = ''
        oldTokenListForChange = []
        newTokens = []
        if byShunit:
            # find shunit in
            oldText = self.tokenManager.getString() # རྒྱ་གར་སྐད་དུ། བོ་དྷི་ས་ཏྭ་ཙརྱ་ཨ་བ་ཏ་ར།
            newText = self.centralWidget.textEdit.toPlainText() # རྒྱ་ག་སྐད་དུ། བོ་དྷི་ས་ཏྭ་ཙརྱ་ཨ་བ་ཏ་ར།
            tokens = self.tokens
            # 最一開始輸入文字，尚未做過 segment
            if not oldText or newText == '':
                self.tokens = self.tokenManager.segment(newText)
            # 有對文字作修改，需針對部分做 segment
            else:
                tokenStart, tokenEnd, afterChangingString = \
                    self.tokenManager.diff(tokens, oldText, newText)
                # 新的字串做 segment
                newTokens = self.tokenManager.segment(afterChangingString)
                if newTokens:
                    oldTokenListForChange = tokens[tokenStart:tokenEnd + 1]

                if tokenStart == tokenEnd and \
                    not (tokenStart == 0) and \
                    not tokens[-1].text in afterChangingString:
#                     start = time.time() ##
                    if newTokens:
                        if (newTokens[0].text == '།'
                            or newTokens[0].text == '\n') \
                            and len(newTokens) > 1:
                            # and() -> 只有一個時，不能從 1 開始
                            self.tokens.extend(newTokens[1:])
                        else:
                            self.tokens.extend(newTokens[0:])
#                     end = time.time() ##
#                     print(f'self.tokens.extend(): {round((end-start) * 1000, 2)}ms') ##
                elif tokenStart == 0 and tokenEnd == 0:
#                     start = time.time() ##
                    string = self.centralWidget.textEdit.toPlainText()
                    self.tokens = self.tokenManager.segment(string)
#                     end = time.time() ##
#                     print(f'no change(toPlainText、segment all text): {round((end-start) * 1000, 2)}ms') ##
                else:
#                     start = time.time() ##
                    self.tokens[tokenStart:tokenEnd + 1] = newTokens
#                     end = time.time() ##
#                     print(f'self.tokens[tokenStart:tokenEnd + 1] = newTokens: {round((end-start) * 1000, 2)}ms') ##

                # 這裡是重新加上新的 token 後，tokenEnd 要重新拿，才能做後面計算如 applyDict
                tokenEnd = tokenStart + len(newTokens)
        else:
            string = self.centralWidget.textEdit.toPlainText()
            self.tokens = self.tokenManager.segment(string)

        start = time.time() ##
        self.refreshView(isHighlight, tokens, tokenStart, tokenEnd, oldTokenListForChange, newTokens)
        end = time.time() ##
        print(f'refreshView: {round((end-start) * 1000, 2)}ms') ##
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

#     @ignoreEvent(QTextEdit.textChanged)
#     def textChanged(self):
#         if self.viewManager.isPlainTextView():
#             string = self.textEdit.toPlainText()
#
#             if any([string.endswith(w) for w in self.SEG_TRIGGERS]):
#                 self.segment()
#                 print('option1')
#                 # self.segment(byBlock=True)
#
#             elif string.endswith('\n'):
#                 self.segment()
#                 print('option2')
#                 # TODO: block mode: bug - if we delete text and try to rewrite new
#                 # text it copies the already saved text.
#                 # self.segment(byBlock=True, breakLine=True)
#
#             elif string == '':
#                 self.segment()
#                 print('option3')

    def fetchLevelProfile(self):
        self.LEVEL_PROFILE_PATH = Setting.objects.get(key='profile_path').value

    def initLevelProfile(self):
        # load last level profile
        Setting.objects.update_or_create(key='profile_path')
        if Setting.objects.get(key='profile_path').value:
            self.fetchLevelProfile()
            self.setLevelProfile()

    # Import Level Profile #
    def loadLevelProfile(self):
        # a profile is a dir containing level lists
        dirPath = QtWidgets.QFileDialog.getExistingDirectory(parent=self, directory=os.path.join(FILES_DIR, 'levels'), options=QtWidgets.QFileDialog.ShowDirsOnly)

        # if dir is selected
        if dirPath != '':
            setting = Setting.objects.get(key='profile_path')
            self.LEVEL_PROFILE_PATH = setting.value = dirPath
            setting.save()

            self.levelTab.levelProfileLabel.setText(pathlib.Path(self.LEVEL_PROFILE_PATH).stem)
            # dirpath string
            self.setLevelProfile()

            # segment in order to update the level attribute of each token
            self.segment()

        # if dir is selected
        else:
            # do nothing
#             print('no path')
            pass


    def setLevelProfile(self):
#         print('I am in setLevelProfile!')
        # clear db
        Token.objects.all().delete()
        # reset level names
        self.levelTab.level1Button.setText(Tabs.LEVEL_NAMES[0])
        self.levelTab.level2Button.setText(Tabs.LEVEL_NAMES[1])
        self.levelTab.level3Button.setText(Tabs.LEVEL_NAMES[2])
        self.levelTab.level4Button.setText(Tabs.LEVEL_NAMES[3])

        # get file paths
        if self.LEVEL_PROFILE_PATH:
            levelFiles = sorted(list(pathlib.Path(self.LEVEL_PROFILE_PATH).glob("*.txt")))
        else:
            return

        if not levelFiles:
            # Token objects are deleted so it'll reset
            self.refreshView()
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
        self.refreshView(isHighlight=True)

    # Import Level List
    def importLevelList(self, level, levelButton):

        # TODO delete DB entries for current level
        #

        # get file path
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select a level list", os.path.join(FILES_DIR, 'levels'), filter="UTF-8 ཡིག་རྐྱང་། (*.txt)")

        if not filePath:
            return
        else:
            self.setLevelList(level, levelButton, filePath)


    def parseLevelFile(self, filePath):

        with open(filePath, encoding='utf-8') as f:
            words = [word[:-1] if word.strip().endswith(('་', '།')) else word.strip()
                     for word in [line.rstrip('\r\n')
                                  for line in f.readlines()]]
        return words

    # @timed(unit='ms')
    def setLevelList(self, level, levelButton, filePath):

        splitFilePath = pathlib.PurePath(filePath).parts

        # get and set file name
        if '' in splitFilePath[:1]:
            return
        else:
            fileName = splitFilePath[len(splitFilePath) - 1]
            levelButton.setText(fileName)

        # get words
        words = self.parseLevelFile(filePath)

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
    def refreshView(self, isHighlight=False, tokens=None, tokenStart=None, tokenEnd=None, oldTokenListForChange=None, newTokens=None):
        """
        Refreshes the view without segmenting
            :param self:
        """
        # Adds token info from the db
        # - level
        # - sense
        self.tokenManager.applyDict(tokenStart, tokenEnd)

        # adjustment rules ... defer to pybo?
        self.tokenManager.matchRules()

        # keep cursor
        textCursor = self.textEdit.textCursor()
        current = self.tokenManager.find(textCursor.position())
        # print(f'current: {current[0]}')

        if current is not None:
            currentToken = current[1]
            distance = textCursor.position() - currentToken.start
#             print(f'current: {current[0]}, {current[1].text}')

        # Sets plain text in textEdit before moving on to highlighting
        text = self.tokenManager.getString() # after tokenize
        textOnEditor = self.textEdit.toPlainText() # text on editor

#         start = time.time() ##
        if textOnEditor == "" or not tokens or isHighlight: # 沒經過 segment，沒有 tokens
            self.textEdit.setPlainText(text)
        elif text != textOnEditor:
#             start2 = time.time() ##
            changes = diff(textOnEditor, text, timelimit=0, checklines=False,
                               counts_only=False)
#             end2 = time.time() ##
#             print(f'refreshView-diff-changes: {round((end2-start2) * 1000, 2)}ms') ##

            # cursor 先設定最前面，隨著 changes 新增/刪除，修改 cursor
            cursor = self.textEdit.textCursor()
            cursor.setPosition(0)
            pos = 0
            for op, string in changes:
                lenOfString = len(string)
                if op == "-" or op == "+":
                    if op == "-": # 刪的情況下，cursor 不用重新定
                        if lenOfString > 1:
                            for e in range(lenOfString):
                                cursor.deleteChar()
                        else:
                            cursor.deleteChar()
                    else:
                        cursor.insertText(string) #會觸發 highlighter
                        pos += lenOfString
                        cursor.setPosition(pos)
                else:
                    pos += len(string)
                cursor.setPosition(pos)

        else: # no any changes, ignore.
            pass
#         end = time.time() ##
#         print(f'refreshView-diff: {round((end-start) * 1000, 2)}ms') ##

        self.textEdit.blockSignals(True)
        self.textEdit.document().blockSignals(True)

        if current is not None:
            textCursor.setPosition(currentToken.start + distance)
        else:
            textCursor.setPosition(len(self.textEdit.toPlainText()))

        self.ignoreCursorPositionChanged(
            self.textEdit.setTextCursor)(textCursor)

        self.textEdit.blockSignals(False)
        self.textEdit.document().blockSignals(False)

        self.refreshCoverage(oldTokenListForChange, newTokens)

        # print([t.text for t in self.tokens])
        # TODO current shunit
        self.statusBar.showMessage(
            '  ' + ' '.join([t.text for t in self.tokens[-19:]]))

    @timed(unit='ms')
    def statistics(self, oldTokenListForChange, newTokens):
        # to do: bug fix -
        # if we press enter twice sentence count reinitializes
        # you need to press on enter for it to recognize that the text editor is empty
        # it considers བོད and བོད་ different - the difference is the tseg (not sure if that is a bug)
        # It always counts the first enter

        # Statistics - analyze the text in the text editor
        # parse through the list and not count the newline
        # for now every newline is considered a completion of one sentence
        def calculateDifferentTypeCountByTokens(tokens):
            wordCount = 0  # number of words written
            sentenceCount = 0  # number of sentence written - each new line is considered one sentnece
            typeCount = 0  # number of words used
            max = 0  # maximum number of words in a sentence - longest sentence
            counts = dict()
            sentenceWordCount = []  # records the number of words in each sentence
            wordSentence = 0  # words in a sentence
            verbsPerSen = 0  # verbs in a sentence
            verbSentence = []  # records the number of verbs in each sentence
            for token in tokens:
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
            return wordCount, sentenceCount, typeCount, max

        if oldTokenListForChange and newTokens:
            wordCountBeDel, sentenceCountBeDel, typeCountBeDel, maxBeDel = calculateDifferentTypeCountByTokens(oldTokenListForChange)
            wordCountBeAdd, sentenceCountBeAdd, typeCountBeAdd, maxBeAdd = calculateDifferentTypeCountByTokens(newTokens)
            wordCount = self.wordCount - wordCountBeDel + wordCountBeAdd
            sentenceCount = self.sentenceCount - sentenceCountBeDel + sentenceCountBeAdd
            typeCount = self.typeCount - typeCountBeDel + typeCountBeAdd
            max  = self.max - maxBeDel + maxBeAdd
        else:
            wordCount, sentenceCount, typeCount, max = calculateDifferentTypeCountByTokens(self.tokens)


        self.wordCount = wordCount
        self.typeCount = typeCount
        self.sentenceCount = sentenceCount
        self.max = max

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
    def refreshCoverage(self, oldTokenListForChange, newTokens):
        if oldTokenListForChange and newTokens:
            tokenNumBeDel = sum(1 for t in oldTokenListForChange if t.type == 'TEXT')
            tokenNumBeAdd = sum(1 for t in newTokens if t.type == 'TEXT')
            tokenNum = self.OldtokenNum - tokenNumBeDel + tokenNumBeAdd
        else:
            tokenNum = sum(1 for t in self.tokens if t.type == 'TEXT')

        self.OldtokenNum = tokenNum
        # print('tokenNum: ', tokenNum)

        self.statistics(oldTokenListForChange, newTokens)

        levelCounter = Counter([
            token.level for token in self.tokens if token.type == 'TEXT'])


        def getLevelPercentage(key):
            if tokenNum == 0:
                return 0
            else:
                # print(f'{key}: {levelCounter[key] / tokenNum * 10000}')
                # Change percentage to
                percentage = levelCounter[key] / tokenNum * 10000
                return percentage

        # update
        if self.tokens:
            self.levelTab.tokenCoverageProgBar.setValue(10000 - getLevelPercentage(None))

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

    language = Setting.objects.filter(key='language')
    if not language:
        Setting.objects.create(
            key='language',
            value='en'
        )
    language = Setting.objects.get(key='language')
    language = language.value
    translation.activate(language)

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
