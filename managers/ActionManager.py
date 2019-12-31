import os
import webbrowser

from PyQt5 import QtGui, QtWidgets

from web.settings import BASE_DIR

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
        action.setFont(self.editor.uiFont)
        if shortcut is not None:
            action.setShortcut(shortcut)
        if statusTip is not None:
            action.setStatusTip(statusTip)
        if triggered is not None:
            action.triggered.connect(triggered)
        return action

    def createActions(self):
        self.newFileAction = self.createAction(
            '&གསར་པ།...', 'new.png',
            shortcut=QtGui.QKeySequence.New,
            statusTip='ཡིག་ཆ་གསར་པ།',
            triggered=self.editor.newFile
        )

        self.openFileAction = self.createAction(
            '&ཁ་འབྱེད།...', 'open.png',
            shortcut=QtGui.QKeySequence.Open,
            statusTip='ཡིག་ཆ་ཁ་འབྱེད།',
            triggered=self.editor.openFile
        )

        self.saveFileAction = self.createAction(
            '&ཉར་ཚགས།...', 'save.png',
            shortcut=QtGui.QKeySequence.Save,
            statusTip='ཡིག་ཆ་ཉར་ཚགས།',
            triggered=self.editor.saveFile
        )

        self.copyAction = self.createAction(
            '&བཤུ།', 'copy.png',
            shortcut=QtGui.QKeySequence.Copy,
            statusTip='གང་འདམ་པའི་ཡི་གེ་ངོ་བཤུས་རྒྱག',
            triggered=self.editor.copy
        )

        self.pasteAction = self.createAction(
            '&སྦྱར།', 'paste.png',
            shortcut=QtGui.QKeySequence.Paste,
            statusTip='ངོ་བཤུས་བྱས་པའི་ཡི་གེ་བསྒྲིག',
            triggered=self.editor.paste
        )

        self.cutAction = self.createAction(
            '&གཏུབ།', 'cut.png',
            shortcut=QtGui.QKeySequence.Cut,
            statusTip='གང་འདམ་པའི་ཡི་གེ་ཡར་ལེན།',
            triggered=self.editor.cut
        )

        self.undoAction = self.createAction(
            '&ཕྱིར་ལྡོག', 'undo.png',
            shortcut=QtGui.QKeySequence.Undo,
            statusTip='རྩོམ་སྒྲིག་གི་བྱ་བ་མཐའ་མ་ཕྱིར་ལྡོག',
            triggered=self.editor.undo
        )

        self.redoAction = self.createAction(
            '&བསྐྱར་བཟོ།', 'redo.png',
            shortcut=QtGui.QKeySequence.Redo,
            statusTip='ཕྱིར་ལྡོག་བྱས་པའི་རྩོམ་སྒྲིག་གི་བྱ་བ་བསྐྱར་བཟོ།',
            triggered=self.editor.redo
        )

        self.tagViewAction = self.createAction(
            '&མཆན་བྱང་།', 'tag.png',
            shortcut=QtGui.QKeySequence('Ctrl+Shift+Space'),
            checkable=True,
            statusTip='ཚིག་གཤིས་དང་མ་ཚིག་ལྟ་བུའི་མཆན་བྱང་སྟོན།',
            triggered=self.editor.toggleTagView
        )

        self.spaceViewAction = self.createAction(
            '&བར་སྟོང་།', 'space.png',
            shortcut=QtGui.QKeySequence('Ctrl+Space'),
            checkable=True,
            statusTip='ཐ་སྙད་སོ་སོར་འབྱེད་པའི་བར་སྟོང་སྟོན།',
            triggered=self.editor.toggleSpaceView
        )


        # self.dictionaryAction = self.createAction(
        #     '&Open Dictionary', 'dictionary.png',
        #     triggered=lambda: self.editor.dictionaryDialog.show()
        # )

        # self.fontPicker = self.createAction(
        #     '&Pick Font', 'font.png',
        #     triggered=self.editor.fontPickerDialog
        # )

        # self.fonts = self.editor.fontP
        # self.editor.fonts.currentFontChanged.connect(self.editor.)

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
                self.copyAction,
                self.pasteAction,
                self.cutAction
            ]
        elif self.MENU_VIEW == menu:
            return [
                self.spaceViewAction,
                self.tagViewAction,
            ]
        elif self.MENU_HELP == menu:
            return []
