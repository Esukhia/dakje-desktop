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

        if not Setting.objects.filter(key='language').exists():
            Setting.objects.create(
                key='language',
                value=value
            )

        # 一開始的，也要顯示上次選擇後的當前語言
        language = Setting.objects.get(key='language')
        if language.value == 'zh-hant':
            self.cb.setCurrentIndex(0)
        elif language.value == 'en':
            self.cb.setCurrentIndex(1)
        else:
            self.cb.setCurrentIndex(2)

    def onSelectionchange(self,i):
        if self.cb.currentText() == 'Chinese':
            value = 'zh-hant'
        elif self.cb.currentText() == 'English':
            value = 'en'
        else:
            value = 'tibetan'

        language = Setting.objects.get(key='language')
        oldLanguage = language.value
        newLanguage = value

#         # 選擇語言後，依然顯示當前語言?
#         languageN = language.value
#         if languageN == 'zh-hant':
#             self.cb.setCurrentIndex(0)
#         elif languageN == 'en':
#             self.cb.setCurrentIndex(1)
#         else:
#             self.cb.setCurrentIndex(2)

        # 設定所選擇的語言
        if language:
            language.value=value
            language.save()

        # 需要更換語言時才顯示提醒
        if oldLanguage != newLanguage:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(str(_("You can change the language until you activate the editor next time.") + '\n' + f'language:{value}'))
            retval = msg.exec_()

        translation.activate(value)


