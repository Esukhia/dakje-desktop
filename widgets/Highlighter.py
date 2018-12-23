from PyQt5 import QtCore, QtGui, QtWidgets

class Highlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent, editor):
        super().__init__(parent)
        self.editor = editor

    def highlightBlock(self, p_str):
        currentBlock = self.currentBlock()

        # the positions here are relative to the current block
        # FIXME: Temporally Highlight All Words
        for token in self.editor.tokens:
            if not token.level:
                continue

            self.setFormat(token.start - currentBlock.position(),
                           token.length,
                           self.editor.formatManager.LEVEL_FORMATS[token.level])


