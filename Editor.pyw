# django setup
import os
import logging
import time
import multiprocessing

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
django.setup()

# editor
import sys

from functools import partial, wraps
from collections import Counter
from PyQt5 import QtCore, QtWidgets, QtGui
from django.db import transaction

from widgets import (MenuBar, ToolBar, StatusBar, CentralWidget,
                     EditTokenDialog, Highlighter, DictionaryEditorWidget)

from managers import ActionManager, TokenManager, ViewManager, FormatManager, Token 
from storage.models import Token
from web.settings import BASE_DIR

# Logger
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Timed decorator
def timed(func):
    """This decorator prints the execution time for the decorated function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug("{} ran in {}s".format(
            func.__name__, round(end - start, 5)))
        return result
    return wrapper

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


class Editor(QtWidgets.QMainWindow):
    BASE_DIR = os.path.dirname(__name__)
    SEGMENT_WORDS = ['་', '།']

    @timed
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initProperties()
        self.initManagers()
        self.initUI()
        self.bindEvents()
        self.setWindowTitle("དག་བྱེད།")
        self.setWindowIcon(QtGui.QIcon(os.path.join(BASE_DIR, "icons", "icon.jpg")))
        self.setWindowState(QtCore.Qt.WindowMaximized)
        # self.wordcount = 0

        self.textEdit.setPlainText = self.ignoreTextChanged(
            self.ignoreCursorPositionChanged(self.textEdit.setPlainText))
        self.textEdit.setSelection = self.ignoreTextChanged(
            self.ignoreCursorPositionChanged(self.textEdit.setSelection))

    def ignoreEvent(self, func, signal, event):
        def _func(*arg, **kwargs):
            signal.disconnect()
            func(*arg, **kwargs)
            signal.connect(event)
        return _func

    def ignoreCursorPositionChanged(self, func):
        return self.ignoreEvent(func,
                                self.textEdit.cursorPositionChanged,
                                self.cursorPositionChanged)

    def ignoreTextChanged(self, func):
        return self.ignoreEvent(func,
                                self.textEdit.textChanged,
                                self.textChanged)

    def initProperties(self):

        self.tokens = []
        self.formats = []
        self.mode = 'Level Mode'  # LEVEL_MODE, EDITOR_MODE
        self.view = None  # PLAIN_TEXT_VIEW, SPACE_VIEW...
        self.filename = None

        self.editTokenDialog = EditTokenDialog(self)
        self.dictionaryDialog = DictionaryEditorWidget(self)


    def initManagers(self):
        self.actionManager = ActionManager(self)
        self.tokenManager = TokenManager(self)
        self.tokenList = Token(self)
        self.viewManager = ViewManager(self)
        self.formatManager = FormatManager(self)

    def initUI(self):
        self.actionManager.createActions()

        self.menuBar = MenuBar(self.actionManager, parent=self)
        self.setMenuBar(self.menuBar)

        self.toolBar = ToolBar(self.actionManager, parent=self)
        self.addToolBar(self.toolBar)

        self.statusBar = StatusBar(parent=self)
        self.setStatusBar(self.statusBar)

        self.centralWidget = CentralWidget(self)         
        self.setCentralWidget(self.centralWidget)

        self.highlighter = Highlighter(self.textEdit.document(), self)

        self.setStyleSheet('QMainWindow{background-color: white}')
        self.textEdit.setStyleSheet(
            'border: none; margin: 10px')

        #default font and font size 
        font = QtGui.QFont()
        font.setFamily("Microsoft Himalaya")
        font.setPointSize(12)
        self.textEdit.setFont(font)

    def bindEvents(self):
        self.bindCursorPositionChanged()
        self.bindTextChanged()
        self.bindLevelButtons()

    def bindCursorPositionChanged(self):
        self.textEdit.cursorPositionChanged.connect(self.cursorPositionChanged)

    def bindTextChanged(self):
        self.textEdit.textChanged.connect(self.textChanged)
    
    def bindLevelButtons(self):
        self.levelTab.level1Button.clicked.connect(
            # partial(self.importRuleList, level=1)
            partial(self.importLevelList, level=1, levelNum = self.levelTab.level1Button)
        )      

        self.levelTab.level2Button.clicked.connect(
            partial(self.importLevelList, level=2, levelNum = self.levelTab.level2Button))

        self.levelTab.level3Button.clicked.connect(
            partial(self.importLevelList, level=3, levelNum = self.levelTab.level3Button))
    
    def closeEvent(self, *args, **kwargs):
        
        import pickle
        with self.bt.pickled_file.open('wb') as f:
            pickle.dump(self.bt.head, f, pickle.HIGHEST_PROTOCOL)

        super().closeEvent(*args, **kwargs)


    # Tool Bar Actions #

    #user can choose their font
    def fontPickerDialog(self):
        font, ok = QtWidgets.QFontDialog.getFont(self.textEdit.font(), self)
        if ok:
            #set the text in the widget to the choosen font 
            self.textEdit.setFont(font)
            

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


    def segment(self, byBlock=False, breakLine=False):
        if byBlock:
            block = self.textEdit.textCursor().block()
            text = block.text()

            if breakLine:
                block = block.previous()
                text = block.text() + '\n'

            tokens = self.tokenManager.segment(text)
            startIndex, endIndex = self.tokenManager.findByBlockIndex(
                block.blockNumber())

            if startIndex is None:
                self.tokens.extend(tokens)
                
            else:
                dself.tokens[startIndex: endIndex + 1] = tokens
        else:
            text = self.centralWidget.textEdit.toPlainText()
            tokens = self.tokenManager.segment(text)
            self.tokens = tokens
            
        self.refreshView()
        
    def resegment(self):
        text = ''.join([token.content for token in self.tokens])
        tokens = self.tokenManager.segment(text)
        self.tokens = tokens
        self.refreshView()

    @property
    def bt(self):
        return self.tokenManager.tokenizer.tok.trie     

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
    def cursorPositionChanged(self):
        cursor = self.textEdit.textCursor()
        position = cursor.position()

        if (self.viewManager.isTagView() and
                not self.editTokenDialog.isVisible()):
            token = self.tokenManager.find(position)[1]

            if token.pos == "OOV":
                self.actionManager.dictionaryAction.trigger()
                self.dictionaryDialog.addWord(content=token.content)
            else:
                self.editTokenDialog.setMode(EditTokenDialog.MODE_UPDATE)
                self.editTokenDialog.setToken(token)
                self.editTokenDialog.show()

        self.showStatus(ln=cursor.blockNumber() + 1,
                        col=cursor.columnNumber() + 1)

    def textChanged(self):
        if self.viewManager.isPlainTextView():
            text = self.textEdit.toPlainText()

            if any([text.endswith(w) for w in self.SEGMENT_WORDS]):
                self.segment()
                # self.segment(byBlock=True)

            elif text.endswith('\n'):
                self.segment()
                # to do: block mode: bug - if we delete content and try to rewrite new 
                # content it copies the already saved content. 
                # self.segment(byBlock=True, breakLine=True)

    # Level List #
    def importLevelList(self, level, levelNum):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self)
        splitFilePath = filePath.split('/')
        
        if '' in splitFilePath[:1]:
            return
        else:
            self.fileName = splitFilePath[len(splitFilePath) - 1]        
            levelNum.setText(self.fileName)
        with open(filePath, encoding='utf-8') as f:
            words = [word[:-1] if word.endswith('་') else word
                     for word in [line.rstrip('\r\n')
                                  for line in f.readlines()]]

        with transaction.atomic():
            for word in words:
                token = Token.objects.get_or_create(
                    content=word, type=Token.TYPE_UPDATE)[0]
                token.level = level
                token.save()

        self.refreshView()

    def importRuleList(self, level):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self)

        with open(filePath, encoding='utf-8') as f:
            rules = [line.rstrip('\r\n') for line in f.readlines()]

        self.matcher.match(self.tokens, rules)

        self.refreshView()

    # Refresh #
    def refreshView(self):
        self.tokenManager.applyDict()
        self.tokenManager.matchRules()

        # keep cursor
        textCursor = self.textEdit.textCursor()
        current = self.tokenManager.find(textCursor.position())

        if current is not None:
            currentToken = current[1]
            distance = textCursor.position() - currentToken.start

        text = self.tokenManager.getString()
        self.textEdit.setPlainText(text)

        if current is not None:
            textCursor.setPosition(currentToken.start + distance)
        else:
            textCursor.setPosition(len(self.textEdit.toPlainText()))

        self.ignoreCursorPositionChanged(
            self.textEdit.setTextCursor)(textCursor)
        self.refreshCoverage()

        # print([t.content for t in self.tokens])
        self.statusBar.showMessage('  ' + ' '.join([t.content for t in self.tokens[-19:]]))

  

    def statistics(self):
        
        #to do: bug fix - 
        # if we press enter twice sentence count reinitializes
        # you need to press on enter for it to recognize that the text editor is empty 
        # it considers བོད and བོད་ different - the difference is the tseg (not sure if that is a bug)
        # It always counts the first enter  

        #Statistics - analyze the content in the text editor 
        
        wordCount = 0 # number of words written
        sentenceCount = 0 # number of sentence written - each new line is considered one sentnece 
        typeCount = 0 # number of words used 
        max = 0 # maximum number of words in a sentence - longest sentence
        counts = dict() 
        sentenceWordCount = [] #records the number of words in each sentence
        wordSentence = 0 # words in a sentence 
        verbsPerSen = 0 # verbs in a sentence
        verbSentence = [] #records the number of verbs in each sentence 

        #parse through the list and not count the newline 
        #for now every newline is considered a completion of one sentence 
        for token in self.tokens:
            if token.content == "།":
                continue
            if token.content != "\n":
                wordCount += 1
                wordSentence += 1
                if token.pos == "VERB":
                    verbsPerSen += 1
                if token.content in counts:
                    continue
                else:
                    counts[token.content] = 1
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

        #frequency - the number of times a token is repeated 
        frequency = Counter([
            token.content for token in self.tokens])
        print("Frequency: ", frequency)
        

        #Updating the Statistics 
        self.levelTab.wordCountLabel.setText(str(wordCount))
        self.levelTab.typeCountLabel.setText(str(typeCount))
        self.levelTab.senCountLabel.setText(str(sentenceCount))
        self.levelTab.maxWordLabel.setText(str(max))
        

    def refreshCoverage(self):
        # To Do: don't count new line and punctuation in word Count (Done)
        #the progress bars take into consideration new line as a token 

        tokenNum = len(self.tokens)
        self.statistics()

        levelCounter = Counter([
            token.level for token in self.tokens])
 
        def getLevelProp(key):
            if tokenNum == 0:
                return 0
            else:
                return levelCounter[key] / tokenNum * 100.0
        
        #updating the progress bar 
        self.levelTab.tokenCoverageProgBar.setValue(100 - getLevelProp(None))
        self.levelTab.levelNoneProgBar.setValue(getLevelProp(None))
        self.levelTab.level1ProgBar.setValue(getLevelProp(1))
        self.levelTab.level2ProgBar.setValue(getLevelProp(2))
        self.levelTab.level3ProgBar.setValue(getLevelProp(3))

        posCounter = Counter([
            token.pos for token in self.tokens])

        posFreq = posCounter.most_common()

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
        else:
            return None

    def showStatus(self, ln=None, col=None):
        self.statusBar.modeLabel.setText(self.mode)
        self.statusBar.viewLabel.setText(self.viewManager.getStatusDisplay())

        if ln and col:
            self.statusBar.lineLabel.setText(
                'Ln {}, Col {}'.format(ln, col))

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
