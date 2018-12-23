from widgets import DictionaryEditorWidget

from PyQt5 import QtCore, QtGui, QtWidgets

class ActionManager:
    MENU_FILE = 1
    MENU_EDIT = 2
    MENU_HELP = 3

    def __init__(self, editor):
        self.editor = editor

    def createAction(self, name, icon,
                     shortcut=None, statusTip=None, triggered=None):
        action = QtWidgets.QAction(QtGui.QIcon(icon), name, self.editor)
        if shortcut is not None:
            action.setShortcut(shortcut)
        if statusTip is not None:
            action.setStatusTip(statusTip)
        if triggered is not None:
            action.triggered.connect(triggered)
        return action

    def createActions(self):
        self.newFileAction = self.createAction(
            '&New...', 'icons/new.png',
            shortcut=QtGui.QKeySequence.New,
            statusTip='Create a new file',
            triggered=self.editor.newFile
        )

        self.openFileAction = self.createAction(
            '&Open...', 'icons/open.png',
            shortcut=QtGui.QKeySequence.Open,
            statusTip='Open a text file',
            triggered=self.editor.openFile
        )

        self.saveFileAction = self.createAction(
            '&Save...', 'icons/save.png',
            shortcut=QtGui.QKeySequence.Save,
            statusTip='Save the current document',
            triggered=self.editor.saveFile
        )

        self.undoAction = self.createAction(
            '&Undo', 'icons/undo.png',
            shortcut=QtGui.QKeySequence.Undo,
            statusTip='Undo the last editing action',
            triggered=self.editor.undo
        )

        self.redoAction = self.createAction(
            '&Redo', 'icons/redo.png',
            shortcut=QtGui.QKeySequence.Redo,
            statusTip='Redo the last editing action',
            triggered=self.editor.segment
        )

        self.tagViewAction = self.createAction(
            '&Toggle Tag View', 'icons/tag.png',
            triggered=self.editor.toggleTagView
        )

        self.spaceViewAction = self.createAction(
            '&Toggle Space View', 'icons/space.png',
            triggered=self.editor.toggleSpaceView
        )

        self.dictionaryAction = self.createAction(
            '&Open Dictionary', 'icons/dictionary.png',
            triggered=lambda: DictionaryEditorWidget(self.editor).show()
        )

    def getToolBarActions(self):
        return [
            [self.newFileAction, self.openFileAction, self.saveFileAction],
            [self.undoAction, self.redoAction],
            [self.spaceViewAction, self.tagViewAction],
            [self.dictionaryAction]
        ]

    def getMenuBarActions(self, menu):
        if self.MENU_FILE == menu:
            return [
                self.newFileAction,
                self.openFileAction,
                self.saveFileAction
            ]
        elif self.MENU_EDIT == menu:
            return [
                self.undoAction,
                self.redoAction,
                self.spaceViewAction,
                self.tagViewAction,
                self.dictionaryAction
            ]
        elif self.MENU_HELP == menu:
            return []
