from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QHBoxLayout, QComboBox, QMessageBox

from django.utils import translation
from django.utils.translation import gettext_lazy as _

from storage.models import Setting
# new file, open file, save file, space view, tag view
class ToolBar(QtWidgets.QToolBar):
    def __init__(self, actionManager, parent=None):
        super().__init__(parent)
        self.actionManager = actionManager
        self.setMovable(False)

        for actions in actionManager.getToolBarActions():
            self.addSeparator()
            for action in actions:
                self.addAction(action)

        layout = QHBoxLayout()
        self.cb = QComboBox()
        self.cb.addItems(["Chinese", "English", "Tibetan"])
        self.cb.currentIndexChanged.connect(self.onSelectionchange)

        self.addWidget(self.cb)

        if self.cb.currentText() == 'Chinese':
            value = 'zh-hant'
        elif self.cb.currentText() == 'English':
            value = 'en'
        else:
            value = 'tibetan'

        language = Setting.objects.filter(key='language')
        if not language:
            Setting.objects.create(
                key='language',
                value=value
            )

    def onSelectionchange(self,i):
        if self.cb.currentText() == 'Chinese':
            value = 'zh-hant'
        elif self.cb.currentText() == 'English':
            value = 'en'
        else:
            value = 'tibetan'

        language = Setting.objects.get(key='language')
        if language:
            language.value=value
            language.save()

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(str(_("You can change the language until you activate the editor next time.")))
        retval = msg.exec_()

        translation.activate(value)


