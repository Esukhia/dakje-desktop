
import os
import json
import zipfile
import re

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from TextFormat import TextFormat

class ProfileManager:
    def __init__(self, parent):
        self.parent = parent

    def saveProfile(self, filePath=None):
        import zipfile
        filenames = []
        setting = []

        for i, textFormat in enumerate(self.parent.textFormatManager.getFormats()):

            if textFormat.type == 'level':

                # list #
                listFilename = textFormat.name + '_' + str(i) + '_list.txt'

                for char in r'\/:*?"<>|':
                    if char in listFilename:
                        listFilename = listFilename.replace(char, '_')

                listFilename = os.path.join(
                    self.parent.SETTINGS_DIRECTORY, listFilename)
                with open(listFilename, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(textFormat.wordList))

                filenames.append(listFilename)

            # rule #

            ruleFilename = textFormat.name + '_' + str(i) + '_rule.txt'

            for char in r'\/:*?"<>|':
                if char in ruleFilename:
                    ruleFilename = ruleFilename.replace(char, '_')

            ruleFilename = os.path.join(
                self.parent.SETTINGS_DIRECTORY, ruleFilename)
            with open(ruleFilename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(textFormat.regexList))

            filenames.append(ruleFilename)

            if textFormat.type == 'level':
                textFormatDict = {
                    'name': textFormat.name,
                    'type': textFormat.type,
                    'color': textFormat.getColorRgba(),
                    'listFilename': os.path.basename(listFilename),
                    'ruleFilename': os.path.basename(ruleFilename),
                }
            else:
                textFormatDict = {
                    'name': textFormat.name,
                    'type': textFormat.type,
                    'color': textFormat.getColorRgba(),
                    'ruleFilename': os.path.basename(ruleFilename),
                }

            setting.append(textFormatDict)

        settingFile = os.path.join(self.parent.SETTINGS_DIRECTORY,
                                   'setting.json')
        with open(settingFile, 'w+', encoding='utf-8') as f:
            f.write(json.dumps(setting))

        if not filePath:
            filePath, _ = QFileDialog.getSaveFileName(
                self.parent, "Choose a file name", '.', "Profile (*.profile)")

        if filePath:
            with zipfile.ZipFile(
                filePath, 'w', compression=zipfile.ZIP_DEFLATED
            ) as zf:
                for filename in filenames:
                    zf.write(filename, arcname=os.path.basename(filename))
                    os.remove(filename)
                zf.write(settingFile, arcname=os.path.basename(settingFile))
                os.remove(settingFile)

    def openProfile(self, filePath=None):
        if not filePath:
            filePath, _ = QFileDialog.getOpenFileName(
                self.parent, "Choose a file name", '.', "Profile (*.profile)")

        if filePath:
            textFormats = []
            try:
                with zipfile.ZipFile(filePath, 'r',
                                     compression=zipfile.ZIP_DEFLATED) as zf:
                    settingFile = os.path.join(self.parent.SETTINGS_DIRECTORY,
                                               'setting.json')
                    setting = json.loads(zf.read(
                        os.path.basename(settingFile)
                    ).decode())

                    for textFormatDict in setting:
                        textFormat = TextFormat(
                            textFormatDict['name'], textFormatDict['type'])
                        textFormat.setColor(QColor(*textFormatDict['color']))

                        if textFormat.type == 'level':
                            textFormat.setupWordList(
                                '', zf.read(textFormatDict['listFilename']
                                            ).decode().split('\r\n'))
                        textFormat.setupRegexList(
                            '', zf.read(textFormatDict['ruleFilename']
                                        ).decode().split('\r\n'))

                        if textFormat.type == 'level':
                            textFormats.append(
                                (textFormat,
                                 textFormatDict['listFilename'].split('/')[-1],
                                 textFormatDict['ruleFilename'].split('/')[-1]))
                        else:
                            textFormats.append(
                                (textFormat,
                                 None,
                                 textFormatDict['ruleFilename'].split('/')[-1]))

            except Exception as e:
                self.msg = QMessageBox()
                self.msg.setIcon(QMessageBox.Warning)
                self.msg.setText("Open the profile failed.\n{}".format(str(e)))
                self.msg.show()

            else:
                # 改 window title
                profileName = filePath.split('/')[-1]
                self.parent.setWindowTitle(
                    re.sub(r'\(.*\)', '(' + profileName + ')',
                           self.parent.windowTitle()))

                self.parent.textFormatManager.clear()
                for textFormat, listName, ruleName in textFormats:
                    self.parent.textFormatManager.insert(textFormat)

                    if textFormat.type == 'level':
                        textFormat.listButton.setText(
                            listName[:10] + '..' if len(
                                listName) > 10 else listName)

                    textFormat.ruleButton.setText(
                        ruleName[:10] + '..' if len(
                            ruleName) > 10 else listName)

                self.parent.highlightViewpoint()
