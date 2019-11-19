import os
import webbrowser

from PyQt5 import QtGui, QtWidgets

from dakje.web.settings import BASE_DIR

class ActionManager:
    MENU_FILE = 1
    MENU_EDIT = 2
    MENU_VIEW = 3
    MENU_HELP = 4

    def __init__(self, editor):
        self.editor = editor

    def createAction(self, name, icon, checkable=False,
                     shortcut=None, statusTip=None, triggered=None):
        iconPath = os.path.join(BASE_DIR, 'icons', icon)
        action = QtWidgets.QAction(QtGui.QIcon(iconPath), name, self.editor)
        action.setCheckable(checkable)
        if shortcut is not None:
            action.setShortcut(shortcut)
        if statusTip is not None:
            action.setStatusTip(statusTip)
        if triggered is not None:
            action.triggered.connect(triggered)
        return action

    def createActions(self):
        self.newFileAction = self.createAction(
            '&New...', 'new.png',
            shortcut=QtGui.QKeySequence.New,
            statusTip='Create a new file',
            triggered=self.editor.newFile
        )

        self.openFileAction = self.createAction(
            '&Open...', 'open.png',
            shortcut=QtGui.QKeySequence.Open,
            statusTip='Open a text file',
            triggered=self.editor.openFile
        )

        self.saveFileAction = self.createAction(
            '&Save...', 'save.png',
            shortcut=QtGui.QKeySequence.Save,
            statusTip='Save the current document',
            triggered=self.editor.saveFile
        )

        self.undoAction = self.createAction(
            '&Undo', 'undo.png',
            shortcut=QtGui.QKeySequence.Undo,
            statusTip='Undo the last editing action',
            triggered=self.editor.undoStk.undo
        )

        self.redoAction = self.createAction(
            '&Redo', 'redo.png',
            shortcut=QtGui.QKeySequence.Redo,
            statusTip='Redo the last editing action',
            triggered=self.editor.undoStk.redo
        )

        self.tagViewAction = self.createAction(
            '&Toggle Tag View', 'tag.png',
            checkable=True,
            triggered=self.editor.toggleTagView
        )

        self.spaceViewAction = self.createAction(
            '&Toggle Space View', 'space.png',
            checkable=True,
            triggered=self.editor.toggleSpaceView
        )


        # self.dictionaryAction = self.createAction(
        #     '&Open Dictionary', 'dictionary.png',
        #     triggered=lambda: self.editor.dictionaryDialog.show()
        # )

        self.openAdminAction = self.createAction(
            '&Open Admin', 'settings.png',
            triggered=lambda: webbrowser.open(
                'http://127.0.0.1:8000/admin')
        )

    def getToolBarActions(self):
        return [
            [self.newFileAction, self.openFileAction, self.saveFileAction],
            #[self.undoAction, self.redoAction],
            [self.spaceViewAction, self.tagViewAction],
            # [self.fontPicker] , 
            # self.dictionaryAction, self.openAdminAction]
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
            ]
        elif self.MENU_VIEW == menu:
            return [
                self.spaceViewAction,
                self.tagViewAction,
            ]
        elif self.MENU_HELP == menu:
            return []
