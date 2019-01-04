
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

    def toggleTagView(self):
        if self.isTagView():
            self.view -= 2
        else:
            self.view += 2

        self.checkReadonly()

    def checkReadonly(self):
        if self.view in (self.PLAIN_TEXT_VIEW, self.SPACE_VIEW):
            self.editor.textEdit.setReadOnly(False)
        else:
            self.editor.textEdit.setReadOnly(True)
