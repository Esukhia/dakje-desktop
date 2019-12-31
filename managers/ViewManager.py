
class ViewManager:
    PLAIN_TEXT_VIEW = 0
    SPACE_VIEW = 1
    TAG_VIEW = 2
    BOTH_VIEW = 3

    def __init__(self, editor):
        self.editor = editor
        self.editor.view = self.PLAIN_TEXT_VIEW

    @property
    def view(self):
        return self.editor.view

    @view.setter
    def view(self, value):
        self.editor.view = value

    def isPlainTextView(self):
        return True if self.view == self.PLAIN_TEXT_VIEW else False

    def isSpaceView(self):
        return True if self.view in (self.SPACE_VIEW, self.BOTH_VIEW) else False

    def isTagView(self):
        return True if self.view in (self.TAG_VIEW, self.BOTH_VIEW) else False

    def toggleSpaceView(self):
        if self.isSpaceView():
            self.view -= 1
        else:
            self.view += 1

        self.checkReadonly()
        self.checkReplaceOK()
        self.editor.showStatus()

    def toggleTagView(self):
        if self.isTagView():
            self.view -= 2
        else:
            self.view += 2

        self.checkReadonly()
        self.checkReplaceOK()
        self.editor.showStatus()

    def checkReadonly(self):
        if self.view in (self.PLAIN_TEXT_VIEW, self.SPACE_VIEW):
            self.editor.textEdit.setReadOnly(False)
        else:
            self.editor.textEdit.setReadOnly(True)

    def checkReplaceOK(self):
        if self.view == self.PLAIN_TEXT_VIEW:
            self.editor.findWidget.replaceBtn.setDisabled(False)
            self.editor.findWidget.replaceAllBtn.setDisabled(False)
        else:
            self.editor.findWidget.replaceBtn.setDisabled(True)
            self.editor.findWidget.replaceAllBtn.setDisabled(True)

    def getStatusDisplay(self):
        if self.view == self.PLAIN_TEXT_VIEW:
            msg = 'ཡིག་རྐྱང་།'
        elif self.view == self.SPACE_VIEW:
            msg = 'བར་སྟོང་།'
        elif self.view == self.TAG_VIEW:
            msg = 'མཆན་བྱང་།'
        else:
            msg = 'Space/Tag View'
        return msg
