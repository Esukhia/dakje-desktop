from PyQt5 import QtCore, QtGui, QtWidgets

class Highlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent, editor):
        super().__init__(parent)
        self.editor = editor

    def highlightBlock(self, p_str):
        currentBlock = self.currentBlock()

        highlightedLevels = self.editor.getHighlightedLevels()

        # the positions here are relative to the current block
        # TODO: Temporally Highlight All Words
        for token in self.editor.tokens:
            if token.level not in highlightedLevels:
                continue

            self.setFormat(
                token.start - currentBlock.position(), token.length,
                self.editor.formatManager.LEVEL_FORMATS[token.level]
            )
