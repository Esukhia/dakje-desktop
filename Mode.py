
class ModeManager:
    def __init__(self, parent):
        self.parent = parent
        self._spaceModeOn = False
        self._tagModeOn = False

    def isTagMode(self):
        return self._tagModeOn

    def isSpaceMode(self):
        return self._spaceModeOn

    def checkIcon(self):
        if self._spaceModeOn or self._tagModeOn:
            self.parent.segmentAction.setEnabled(False)
        else:
            self.parent.segmentAction.setEnabled(True)

    def setText(self):
        # print([w.content for w in self.parent.wordManager.getWords()])
        text = []
        end = 0
        for word in self.parent.wordManager.getWords():
            start = end
            end = start + len(word.content)

            text.append(word.content)
            word.start = start

            if self._tagModeOn and word.content != '\n':
                text.append('/')
                text.append(word.partOfSpeech)
                word.tagIsOn = True
                end += word.partOfSpeechLen
            else:
                word.tagIsOn = False

            if self._spaceModeOn:
                text.append(' ')
                end += 1

        self.parent.textEdit.textChanged.disconnect()
        self.parent.textEdit.setPlainText(''.join(text))
        self.parent.textEdit.textChanged.connect(
            self.parent.eventHandler.textChanged)

    def switchDisplayMode(self, mode):
        if not self._spaceModeOn and not self._tagModeOn:
            self.parent.segment()

        if mode == 'Spaces':
            self._spaceModeOn = not self._spaceModeOn
        elif mode == 'Tags':
            self._tagModeOn = not self._tagModeOn

        self.setText()
        self.parent.highlightViewpoint(
            currentBlock=self.parent.textEdit.document().firstBlock())
        self.checkIcon()
